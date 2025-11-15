from django.db import models

class Game(models.Model):
    """Represents a single-player Jeopardy game session"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    phase = models.CharField(
        max_length=20,
        choices=[
            ('SETUP', 'Setup'),
            ('PLAYING', 'Playing'),
            ('COMPLETE', 'Complete')
        ],
        default='SETUP'
    )
    
    def __str__(self):
        return f"Game {self.id} - Score: {self.score}"


class Category(models.Model):
    """Represents a category on the Jeopardy board"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='categories')
    title = models.CharField(max_length=100)
    order = models.IntegerField(default=0)  # Position on board
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """Represents a Jeopardy question"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    value = models.IntegerField(default=200)  # Jeopardy values: 200, 400, 600, 800, 1000
    question_text = models.TextField()
    answer_text = models.TextField()
    is_answered = models.BooleanField(default=False)
    player_correct = models.BooleanField(default=False)  # Did the player get it right?
    
    def __str__(self):
        return f"{self.category.title} - ${self.value}: {self.question_text[:50]}"
