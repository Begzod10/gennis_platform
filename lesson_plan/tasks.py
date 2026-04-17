import json
import logging
import os
from datetime import timedelta, datetime

from celery import shared_task
from django.utils import timezone

from lesson_plan.models import LessonPlan, LessonPlanFile
from school_time_table.models import ClassTimeTable

logger = logging.getLogger(__name__)


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
            date=timetable.date
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
    """Return plain text from a .txt, .pdf, or .docx file."""
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
