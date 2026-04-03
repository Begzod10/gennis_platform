
import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.environ.get("PROXY_API_KEY", ""),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)


def analyze_short_answers(question_text: str, answers: list[str]) -> dict:

    if not answers:
        return {"ai_summary": None, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}}

    answers_text = "\n".join(f"- {a}" for a in answers if a.strip())

    prompt = f"""Quyidagi so'rovnoma savoli bo'yicha o'quvchilar/ota-onalar yozgan javoblarni tahlil qil.

Savol: {question_text}

Javoblar:
{answers_text}

Quyidagi JSON formatida javob ber (faqat JSON, boshqa hech narsa yozma):
{{
  "ai_summary": "Javoblarning qisqa umumiy xulosasi (2-3 gap, o'zbek tilida)",
  "sentiment": {{
    "positive": <ijobiy javoblar foizi, 0-100 orasida int>,
    "neutral": <neytral javoblar foizi, 0-100 orasida int>,
    "negative": <salbiy javoblar foizi, 0-100 orasida int>
  }}
}}

Shartlar:
- positive + neutral + negative = 100 bo'lishi shart
- ai_summary o'zbek tilida bo'lsin
- Faqat JSON qaytargil, markdown yoki izoh yozma
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)

        s = result.get("sentiment", {})
        total = s.get("positive", 0) + s.get("neutral", 0) + s.get("negative", 0)
        if total != 100:
            diff = 100 - total
            s["neutral"] = s.get("neutral", 0) + diff

        return {
            "ai_summary": result.get("ai_summary"),
            "sentiment": s,
        }

    except json.JSONDecodeError as e:
        logger.error(f"AI JSON parse error: {e} | raw: {raw}")
        return {"ai_summary": None, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}}
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return {"ai_summary": None, "sentiment": {"positive": 0, "neutral": 0, "negative": 0}}