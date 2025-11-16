#!/usr/bin/env python
"""
Test script: Create a game and print all generated questions
Usage: python manage.py shell < test_generation.py
"""

from main.game_logic import JeopardyGame
from main.models import Game, Category, Question
import json

# Delete previous test games
Game.objects.all().delete()

# Create a new game
print("Creating new game with Gemini generation...\n")
game_logic = JeopardyGame()
game = game_logic.create_new_game(num_categories=6)

print(f"✓ Game created: ID {game.id}\n")

# Fetch and display all categories and questions
categories = game.categories.all()

for category in categories:
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category.title}")
    print(f"{'='*60}")
    
    questions = category.questions.all().order_by('value')
    for q in questions:
        print(f"\n  ${q.value}")
        print(f"  Q: {q.question_text}")
        print(f"  A: {q.answer_text}")

# Also print as JSON
print(f"\n\n{'='*60}")
print("FULL BOARD STATE (JSON):")
print(f"{'='*60}\n")
board = game_logic.get_board_state()
print(json.dumps(board, indent=2))

print(f"\n✓ Game ID: {game.id}")
print(f"✓ Total questions: {Question.objects.filter(category__game=game).count()}")
