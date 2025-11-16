from google import genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    print("Gemini response:", response.text)
    return response.text


def generate_mcq_via_gemini(topic: str = None) -> dict | None:
    """Ask Gemini to generate a single multiple-choice question in JSON.

    Returns a dict with keys: text, choices (list of 4), correct (A-D), difficulty (int 1-5)
    or None if generation/parsing failed.
    """
    prompt_lines = [
        "Generate a single multiple-choice question suitable for a quiz game.",
        "Respond ONLY with a JSON object with these fields:\n",
        "  - text: the question text string\n",
        "  - choices: an array of 4 answer strings in order\n",
        "  - correct: one of 'A','B','C','D'\n",
        "  - difficulty: integer 1-5 (1=easy,5=hard)\n",
        "Do not include any extra commentary or formatting.\n",
    ]
    if topic:
        prompt_lines.append(f"Topic: {topic}\n")

    prompt = "\n".join(prompt_lines)
    try:
        raw = ask_gemini(prompt)
        # Try to parse JSON directly
        obj = json.loads(raw)
        # validate
        if not isinstance(obj.get("choices"), list) or len(obj["choices"]) != 4:
            logger.warning("Gemini returned invalid choices format")
            return None
        return {
            "text": obj.get("text", "").strip(),
            "choices": [c.strip() for c in obj.get("choices", [])],
            "correct": obj.get("correct", "").strip(),
            "difficulty": int(obj.get("difficulty", 3)),
        }
    except Exception as exc:
        logger.exception("Failed to generate/parse question from Gemini: %s", exc)
        return None