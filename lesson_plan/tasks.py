import json
import logging
import os
from datetime import timedelta, datetime

from celery import shared_task
from django.utils import timezone
from openai import OpenAI

from lesson_plan.models import LessonPlan, LessonPlanFile
from school_time_table.models import ClassTimeTable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert education evaluator. You will receive a teacher's lesson plan and must evaluate it.

Evaluation criteria:
- Objective clarity (is the lesson objective clear and measurable?)
- Main lesson content (is the content well-structured and appropriate?)
- Homework relevance (does homework reinforce the lesson?)
- Assessment quality (are assessments aligned with objectives?)
- Activities engagement (are activities interactive and effective?)
- Resources appropriateness (are resources suitable for the lesson?)

You must respond in JSON format with exactly two fields:
{
    "ball": <integer from 1 to 10>,
    "conclusion": "<brief evaluation summary in Uzbek language explaining strengths and weaknesses>"
}

Respond ONLY with valid JSON. No extra text."""

USER_PROMPT_TEMPLATE = """Evaluate this lesson plan:

Objective: {objective}
Main Lesson: {main_lesson}
Homework: {homework}
Assessment: {assessment}
Activities: {activities}
Resources: {resources}"""


def evaluate_lesson_plan(lesson_plan):
    client = OpenAI(
        api_key=os.environ.get("PROXY_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://lively-breeze-0247.rimefara22.workers.dev/v1"),
    )

    user_prompt = USER_PROMPT_TEMPLATE.format(
        objective=lesson_plan.objective or "",
        main_lesson=lesson_plan.main_lesson or "",
        homework=lesson_plan.homework or "",
        assessment=lesson_plan.assessment or "",
        activities=lesson_plan.activities or "",
        resources=lesson_plan.resources or "",
    )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=1000,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    result = json.loads(content)
    score = int(result["ball"])
    conclusion = str(result["conclusion"])

    if score < 1 or score > 10:
        logger.warning(f"Score out of range: {score}")
        score = max(1, min(10, score))

    return score, conclusion


@shared_task(bind=True, max_retries=3, default_retry_delay=120, name='check_lesson_plans')
def check_lesson_plans(self):
    try:

        today = datetime.now().date()
        three_days_ahead = today + timedelta(days=3)

        lesson_plans = LessonPlan.objects.filter(
            ball__isnull=True,
            objective__isnull=False,
            main_lesson__isnull=False,
            homework__isnull=False,
            date__range=[today, three_days_ahead]
        )

        if not lesson_plans.exists():
            logger.info("No unscored lesson plans found")
            return {"status": "success", "checked": 0}

        checked = 0
        errors = 0

        for lesson_plan in lesson_plans:
            try:
                score, conclusion = evaluate_lesson_plan(lesson_plan)
                lesson_plan.ball = score
                lesson_plan.conclusion = conclusion
                lesson_plan.save(update_fields=["ball", "conclusion"])
                checked += 1
                logger.info(f"Lesson plan {lesson_plan.id} scored: {score}/10")
            except (ValueError, json.JSONDecodeError, KeyError, Exception) as e:
                errors += 1
                logger.error(f"Error scoring lesson plan {lesson_plan.id}: {e}")

        logger.info(f"Checked {checked} lesson plans, {errors} errors")
        return {"status": "success", "checked": checked, "errors": errors}

    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc)


@shared_task
def create_lesson_plans():
    now = datetime.now()
    start_date = now.date()
    end_date = start_date + timedelta(days=4)

    timetable_qs = (
        ClassTimeTable.objects
        .filter(date__range=[start_date, end_date])
        .select_related("teacher")
        .distinct("group_id", "flow_id", "teacher_id", "date")
    )

    for timetable in timetable_qs:
        if not timetable.teacher:
            continue

        if bool(timetable.group_id) == bool(timetable.flow_id):
            continue

        LessonPlan.objects.get_or_create(
            group_id=timetable.group_id,
            flow_id=timetable.flow_id,
            teacher_id=timetable.teacher_id,
            date=timetable.date,
            hour_id_id=timetable.hours_id,
            subject_id=timetable.subject_id,

        )


@shared_task(bind=True, max_retries=2)
def review_lesson_plan_file(self, lesson_plan_file_id: int) -> dict:
    """
    Read the uploaded lesson plan file, send its text to the AI,
    parse the score + feedback, and save back to LessonPlanFile.

    Supported formats: .txt, .pdf, .docx
    Score is 0-100; feedback is in Uzbek.
    """
    try:
        lp_file = LessonPlanFile.objects.select_related("teacher__user", "term").get(id=lesson_plan_file_id)
    except LessonPlanFile.DoesNotExist:
        logger.error("LessonPlanFile %s not found", lesson_plan_file_id)
        return {"success": False, "detail": "Not found"}

    lp_file.status = LessonPlanFile.Status.CHECKING
    lp_file.save(update_fields=["status"])

    # ── Extract text from file ──────────────────────────────────────────────
    try:
        text = _extract_text(lp_file.file)
    except Exception as exc:
        logger.exception("Text extraction failed for LessonPlanFile %s", lesson_plan_file_id)
        lp_file.status = LessonPlanFile.Status.FAILED
        lp_file.feedback = f"Fayldan matn o'qib bo'lmadi: {exc}"
        lp_file.save(update_fields=["status", "feedback"])
        return {"success": False, "detail": str(exc)}

    if not text.strip():
        lp_file.status = LessonPlanFile.Status.FAILED
        lp_file.feedback = "Fayl bo'sh yoki o'qib bo'lmaydigan format."
        lp_file.save(update_fields=["status", "feedback"])
        return {"success": False, "detail": "Empty file"}

    # ── Call AI ─────────────────────────────────────────────────────────────
    try:
        result = _ai_review(text)
    except Exception as exc:
        logger.exception("AI review failed for LessonPlanFile %s", lesson_plan_file_id)
        lp_file.status = LessonPlanFile.Status.FAILED
        lp_file.feedback = f"AI xatolik: {exc}"
        lp_file.save(update_fields=["status", "feedback"])
        raise self.retry(exc=exc, countdown=30)

    lp_file.score = result["score"]
    lp_file.feedback = result["feedback"]
    lp_file.status = LessonPlanFile.Status.DONE
    lp_file.reviewed_at = timezone.now()
    lp_file.save(update_fields=["score", "feedback", "status", "reviewed_at"])

    logger.info("LessonPlanFile %s reviewed: score=%s", lesson_plan_file_id, result["score"])
    return {"success": True, "score": result["score"]}


# ── Helpers ─────────────────────────────────────────────────────────────────

def _extract_text(file_field) -> str:
    """Return plain text from a .txt, .pdf, .docx, or .xlsx file."""
    name = file_field.name.lower()

    with file_field.open("rb") as f:
        raw = f.read()

    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")

    if name.endswith(".pdf"):
        try:
            import pypdf
            import io
            reader = pypdf.PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            raise ImportError("pypdf not installed. Run: pip install pypdf")

    if name.endswith(".docx"):
        try:
            import docx
            import io
            doc = docx.Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

    if name.endswith(".xlsx"):
        try:
            import openpyxl
            import io
            wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
            lines = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    line = "\t".join(str(c) if c is not None else "" for c in row)
                    if line.strip():
                        lines.append(line)
            return "\n".join(lines)
        except ImportError:
            raise ImportError("openpyxl not installed. Run: pip install openpyxl")

    raise ValueError(f"Unsupported file format: {name}")


def _ai_review(text: str) -> dict:
    """Send lesson plan text to AI and return {score, feedback}."""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("PROXY_API_KEY", ""),
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )

    # Truncate to avoid token limits
    truncated = text[:6000]

    prompt = f"""Quyidagi dars rejasini (lesson plan) ko'rib chiq va baholа.

Dars rejasi matni:
\"\"\"
{truncated}
\"\"\"

Quyidagi mezonlar bo'yicha baho ber:
1. Maqsad va vazifalar aniqligi (0-20 ball)
2. Mavzuning o'quv dasturiga muvofiqligi (0-20 ball)
3. Dars bosqichlari to'liqligi (kirish, asosiy qism, yakunlash) (0-20 ball)
4. Baholash usullari va mezonlari (0-20 ball)
5. Til va ifoda savodxonligi (0-20 ball)

Faqat JSON formatida javob ber:
{{
  "score": <umumiy ball 0-100 orasida butun son>,
  "feedback": "<kuchli tomonlari va kamchiliklari haqida o'zbek tilida 3-5 gap>"
}}

Faqat JSON qaytargil, boshqa hech narsa yozma."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=600,
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    result = json.loads(raw)
    score = max(0, min(100, int(result.get("score", 0))))
    feedback = result.get("feedback", "")
    return {"score": score, "feedback": feedback}
