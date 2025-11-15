# main/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .game_logic import JeopardyGame
from .models import Game, Question


def home(request):
    """Home page"""
    return render(request, "main/index.html", {"title": "Jeopardy Game"})


def new_game(request):
    """Create a new Jeopardy game"""
    game_logic = JeopardyGame()
    game = game_logic.create_new_game(num_categories=6)
    
    return redirect('game_board', game_id=game.id)


def game_board(request, game_id):
    """Display the active game board"""
    try:
        game = Game.objects.get(id=game_id)
        game_logic = JeopardyGame(game_id)
        
        context = {
            'game_id': game_id,
            'board_state': game_logic.get_board_state(),
            'current_score': game_logic.get_score(),
            'game_phase': game.phase,
        }
        
        return render(request, "main/game_board.html", context)
    except Game.DoesNotExist:
        return redirect('home')


def get_question(request, question_id):
    """Get question details (AJAX)"""
    try:
        question = Question.objects.get(id=question_id)
        return JsonResponse({
            'id': question.id,
            'value': question.value,
            'question_text': question.question_text,
            'answer_text': question.answer_text,
            'category': question.category.title,
        })
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)


def submit_answer(request, game_id, question_id):
    """Handle answer submission"""
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        
        is_correct = data.get('is_correct', False)
        
        game_logic = JeopardyGame(game_id)
        new_score = game_logic.answer_question(question_id, is_correct)
        
        # Check if game is complete
        is_complete = game_logic.is_board_complete()
        
        if is_complete:
            game = game_logic.game
            game.phase = 'COMPLETE'
            game.save()
        
        response_data = {
            'success': True,
            'new_score': new_score,
            'game_complete': is_complete,
        }
        
        if is_complete:
            response_data['final_stats'] = game_logic.get_final_stats()
        
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_game_state_api(request, game_id):
    """API endpoint to get current game state"""
    try:
        game_logic = JeopardyGame(game_id)
        
        return JsonResponse({
            'board_state': game_logic.get_board_state(),
            'current_score': game_logic.get_score(),
            'game_phase': game_logic.game.phase,
            'board_complete': game_logic.is_board_complete(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def game_complete(request, game_id):
    """Show final results"""
    try:
        game = Game.objects.get(id=game_id)
        game_logic = JeopardyGame(game_id)
        
        context = {
            'game_id': game_id,
            'final_stats': game_logic.get_final_stats(),
        }
        
        return render(request, "main/game_complete.html", context)
    except Game.DoesNotExist:
        return redirect('home')
