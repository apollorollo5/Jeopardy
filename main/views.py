from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import models
from . import utils
from django.conf import settings


def home(request):
    """Landing page. Shows Start/Exit and an Admin link."""
    return render(request, "main/index.html", {})


def start_game(request):
    """Create a new Game and redirect to the first question."""
    player_name = request.POST.get("player_name") or request.GET.get("player_name", "")
    # ensure we have enough questions before starting
    min_q = getattr(settings, "AUTOGEN_MIN_QUESTIONS", 8)
    try:
        # run generation in background so the request is non-blocking
        utils.ensure_min_questions_async(min_q)
    except Exception:
        # generation can fail (no API key or network); keep going with existing questions
        pass

    game = models.Game.objects.create(
        player_name=player_name, status=models.Game.STATUS_ACTIVE, difficulty_pref=request.GET.get("difficulty")
    )
    return redirect("main:question", game_id=game.id)


def _get_next_question_for_game(game: models.Game):
    # use improved selection from utils (randomization + difficulty filter)
    return utils.select_next_question(game)


def question_view(request, game_id: int):
    game = get_object_or_404(models.Game, pk=game_id)
    if game.status != models.Game.STATUS_ACTIVE:
        return redirect("main:score", game_id=game.id)

    question = _get_next_question_for_game(game)
    if not question:
        game.finish()
        return redirect("main:score", game_id=game.id)

    return render(request, "main/game.html", {"game": game, "question": question})


@require_POST
def answer_view(request, game_id: int):
    game = get_object_or_404(models.Game, pk=game_id)
    question_id = int(request.POST.get("question_id"))
    selected = request.POST.get("selected_choice")
    question = get_object_or_404(models.Question, pk=question_id)

    correct = (selected == question.correct_choice)
    pa = models.PlayerAnswer.objects.create(
        game=game, question=question, selected_choice=selected, correct=correct
    )
    if correct:
        game.score = game.score + 1
        game.save()

    # go to next question
    return redirect("main:question", game_id=game.id)


def score_view(request, game_id: int):
    game = get_object_or_404(models.Game, pk=game_id)
    answers = game.answers.select_related("question").all()
    return render(request, "main/score.html", {"game": game, "answers": answers})
