from django.core.management.base import BaseCommand

from main import models


SAMPLE = [
    {
        "category": "General",
        "text": "What planet is known as the Red Planet?",
        "choices": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct": "B",
    },
    {
        "category": "Science",
        "text": "What is the chemical symbol for water?",
        "choices": ["O2", "H2O", "CO2", "HO"],
        "correct": "B",
    },
    {
        "category": "Math",
        "text": "What is 2 + 2?",
        "choices": ["3", "4", "5", "22"],
        "correct": "B",
    },
    {
        "category": "History",
        "text": "Who was the first president of the United States?",
        "choices": ["Abraham Lincoln", "Thomas Jefferson", "George Washington", "John Adams"],
        "correct": "C",
    },
]


class Command(BaseCommand):
    help = "Seed the database with example categories and questions for local development."

    def handle(self, *args, **options):
        created = 0
        for item in SAMPLE:
            cat_name = item["category"]
            cat, _ = models.Category.objects.get_or_create(name=cat_name)

            # check for existing identical question text
            if models.Question.objects.filter(text=item["text"]).exists():
                self.stdout.write(f"Question already exists: {item['text']}")
                continue

            q = models.Question.objects.create(
                category=cat,
                text=item["text"],
                choice_a=item["choices"][0],
                choice_b=item["choices"][1],
                choice_c=item["choices"][2],
                choice_d=item["choices"][3],
                correct_choice=item["correct"],
            )
            created += 1
            self.stdout.write(f"Created question id={q.id}: {q.text[:60]}")

        self.stdout.write(self.style.SUCCESS(f"Seeding complete ({created} created)."))
