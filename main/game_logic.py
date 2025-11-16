"""
Core Jeopardy game logic for single-player mode
"""

from .models import Game, Category, Question
from .gemini_client import ask_gemini
from django.utils import timezone


class JeopardyGame:
    """Single-player Jeopardy game engine"""
    
    def __init__(self, game_id: int = None):
        """Initialize with a game ID, or None for new game"""
        if game_id:
            self.game = Game.objects.get(id=game_id)
        else:
            self.game = None
    
    def create_new_game(self, num_categories: int = 6) -> Game:
        """
        Create a new Jeopardy game
        - Create game instance
        - Generate categories and questions
        - Set initial score to 0
        """
        # Create game
        self.game = Game.objects.create(score=0, phase='PLAYING')
        
        # Generate categories and questions using Gemini
        self._generate_categories_and_questions(num_categories)
        
        return self.game
    
    def _generate_categories_and_questions(self, num_categories: int):
        """
        Use Gemini to generate random Jeopardy categories and questions.
        Falls back to dummy questions if Gemini fails.
        """
        from .gemini_client import ask_gemini_json
        import logging
        
        logger = logging.getLogger(__name__)
        
        prompt = f"""You will respond with ONLY valid JSON, no markdown, no explanation.

Generate {num_categories} Jeopardy categories. Each category has a "title" and "questions" array with exactly 5 questions.
Each question has: value (200,400,600,800,1000), question (string), answer (string).

{{
  "categories": [
    {{
      "title": "CATEGORY_TITLE",
      "questions": [
        {{"value": 200, "question": "Q?", "answer": "A"}},
        {{"value": 400, "question": "Q?", "answer": "A"}},
        {{"value": 600, "question": "Q?", "answer": "A"}},
        {{"value": 800, "question": "Q?", "answer": "A"}},
        {{"value": 1000, "question": "Q?", "answer": "A"}}
      ]
    }}
  ]
}}

Make questions fun, interesting, varied difficulty, family-friendly."""
        
        try:
            # Try to get JSON from Gemini
            response_data = ask_gemini_json(prompt)
            
            # Validate and create categories/questions
            if 'categories' not in response_data:
                raise ValueError("Missing 'categories' key in response")
            
            for idx, cat_data in enumerate(response_data['categories']):
                category = Category.objects.create(
                    game=self.game,
                    title=cat_data.get('title', f'Category {idx+1}'),
                    order=idx
                )
                
                # Create questions (validate each one)
                for q_data in cat_data.get('questions', []):
                    if all(k in q_data for k in ['value', 'question', 'answer']):
                        Question.objects.create(
                            category=category,
                            value=q_data['value'],
                            question_text=q_data['question'],
                            answer_text=q_data['answer']
                        )
            
            logger.info(f"✓ Generated {num_categories} categories from Gemini")
        
        except Exception as e:
            logger.warning(f"Gemini generation failed: {e}. Using fallback dummy questions.")
            self._create_dummy_categories(num_categories)
    
    def _create_dummy_categories(self, num_categories: int):
        """
        Create placeholder categories/questions if Gemini fails
        (Useful for testing without API key)
        """
        categories_data = [
            ("Science", [
                ("What is the chemical symbol for gold?", "Au"),
                ("How many planets are in our solar system?", "Eight"),
                ("What is the speed of light?", "300,000 km/s"),
                ("What gas do plants use for photosynthesis?", "Carbon dioxide"),
                ("What is the smallest bone in the human body?", "Stapes (in the ear)"),
            ]),
            ("History", [
                ("In what year did World War II end?", "1945"),
                ("Who was the first President of the US?", "George Washington"),
                ("What ancient structure is located in Giza, Egypt?", "The Great Pyramid"),
                ("In what year did the Titanic sink?", "1912"),
                ("Who invented the printing press?", "Johannes Gutenberg"),
            ]),
            ("Geography", [
                ("What is the capital of France?", "Paris"),
                ("Which is the largest continent?", "Asia"),
                ("What is the longest river in the world?", "The Nile"),
                ("How many countries are in the European Union?", "27"),
                ("What is the capital of Japan?", "Tokyo"),
            ]),
            ("Literature", [
                ("Who wrote 'Romeo and Juliet'?", "William Shakespeare"),
                ("What is the first book in the Harry Potter series?", "The Philosopher's Stone"),
                ("Who wrote '1984'?", "George Orwell"),
                ("What is the name of Sherlock Holmes's companion?", "Dr. Watson"),
                ("Who wrote 'Pride and Prejudice'?", "Jane Austen"),
            ]),
            ("Sports", [
                ("How many players are on a basketball team on the court?", "Five"),
                ("In what year were the first modern Olympics held?", "1896"),
                ("What is the maximum break in snooker?", "147"),
                ("How many holes are on a standard golf course?", "18"),
                ("Which country has won the most FIFA World Cups?", "Brazil"),
            ]),
            ("Movies", [
                ("What year was the first Star Wars film released?", "1977"),
                ("Who directed 'The Shawshank Redemption'?", "Frank Darabont"),
                ("What is the name of the main character in The Matrix?", "Neo"),
                ("In what year was Avatar released?", "2009"),
                ("Who won the Oscar for Best Actor in 2020?", "Joaquin Phoenix"),
            ]),
        ]
        
        for idx, (cat_title, questions) in enumerate(categories_data[:num_categories]):
            category = Category.objects.create(
                game=self.game,
                title=cat_title,
                order=idx
            )
            
            for q_idx, (q_text, a_text) in enumerate(questions):
                value = (q_idx + 1) * 200  # 200, 400, 600, 800, 1000
                Question.objects.create(
                    category=category,
                    value=value,
                    question_text=q_text,
                    answer_text=a_text
                )
        
        print("✓ Dummy questions created (Gemini not available)")
    
    def get_question(self, question_id: int) -> Question:
        """Get a specific question"""
        return Question.objects.get(id=question_id)
    
    def answer_question(self, question_id: int, is_correct: bool) -> int:
        """
        Record an answer to a question
        - If correct: add points to game score
        - If incorrect: subtract points
        
        Returns the updated score
        """
        question = Question.objects.get(id=question_id)
        
        if question.is_answered:
            return self.game.score  # Already answered, no change
        
        question.is_answered = True
        question.player_correct = is_correct
        question.save()
        
        if is_correct:
            self.game.score += question.value
        else:
            self.game.score -= question.value
        
        self.game.save()
        return self.game.score
    
    def get_board_state(self) -> dict:
        """
        Return the current state of the board
        Shows which questions are answered/unanswered
        
        Returns:
        {
            "Category Name": {
                "questions": [
                    {"value": 200, "is_answered": False, "id": 1},
                    ...
                ]
            }
        }
        """
        categories = self.game.categories.all()
        board = {}
        
        for category in categories:
            board[category.title] = {
                'questions': []
            }
            for question in category.questions.all().order_by('value'):
                board[category.title]['questions'].append({
                    'value': question.value,
                    'is_answered': question.is_answered,
                    'id': question.id
                })
        
        return board
    
    def get_score(self) -> int:
        """Get the current score"""
        return self.game.score
    
    def is_board_complete(self) -> bool:
        """Check if all questions have been answered"""
        unanswered = Question.objects.filter(
            category__game=self.game,
            is_answered=False
        ).count()
        
        return unanswered == 0
    
    def get_final_stats(self) -> dict:
        """Get final game statistics"""
        total_questions = Question.objects.filter(category__game=self.game).count()
        correct_answers = Question.objects.filter(
            category__game=self.game,
            is_answered=True,
            player_correct=True
        ).count()
        
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return {
            'final_score': self.game.score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': f"{accuracy:.1f}%"
        }
