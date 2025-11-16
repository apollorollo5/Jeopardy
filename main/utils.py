from django.conf import settings
from . import models
from .gemini_client import generate_mcq_via_gemini
import logging

logger = logging.getLogger(__name__)


def ensure_min_questions(min_count: int = 10, topic: str | None = None, max_attempts: int = 30) -> int:
    """Ensure the database has at least `min_count` questions.

    Returns the number of questions present after the operation.
    Attempts to call Gemini to generate new questions until the count reaches min_count
    or until max_attempts is exhausted.
    """
    current = models.Question.objects.count()
    attempts = 0
    while current < min_count and attempts < max_attempts:
        attempts += 1
        logger.info("Need questions: have=%s want=%s (attempt %s)", current, min_count, attempts)
        qdata = generate_mcq_via_gemini(topic=topic)
        if not qdata:
            logger.warning("Gemini did not return a valid question on attempt %s", attempts)
            continue

        try:
            # avoid creating duplicates by text
            text = qdata.get("text", "").strip()
            if not text or models.Question.objects.filter(text__iexact=text).exists():
                logger.info("Skipping duplicate or empty question text on attempt %s", attempts)
                continue

            models.Question.objects.create(
                category=None,
                text=text,
                choice_a=qdata["choices"][0],
                choice_b=qdata["choices"][1],
                choice_c=qdata["choices"][2],
                choice_d=qdata["choices"][3],
                correct_choice=qdata["correct"],
                difficulty=qdata.get("difficulty", None),
            )
            current = models.Question.objects.count()
        except Exception as exc:
            logger.exception("Failed to save generated question: %s", exc)
            continue

    return current


def select_next_question(game: models.Game):
    """Select the next question for a game.

    Behavior:
    - If the game has a difficulty_pref, filter by that difficulty.
    - Randomize the order of available questions.
    - Exclude already answered questions for this game.
    """
    qs = models.Question.objects.all()
    if game.difficulty_pref:
        qs = qs.filter(difficulty=game.difficulty_pref)

    answered_ids = game.answers.values_list("question_id", flat=True)
    qs = qs.exclude(id__in=answered_ids)

    # Randomize using order_by('?') for small datasets; if large, replace with more efficient strategy
    return qs.order_by("?").first()


def ensure_min_questions_async(min_count: int = 10, topic: str | None = None, max_attempts: int = 30):
    """Run ensure_min_questions in a background thread and return the Thread object.

    This is a lightweight, best-effort async helper for development. For production
    use a proper background worker (Celery, RQ, etc.).
    """
    import threading

    thread = threading.Thread(
        target=ensure_min_questions, args=(min_count, topic, max_attempts), daemon=True
    )
    thread.start()
    logger.info("Started background question generator thread (daemon=%s)", thread.daemon)
    return thread
