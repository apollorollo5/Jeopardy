from django.db import models
from django.utils import timezone


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return self.name


class Question(models.Model):
	CHOICE_A = "A"
	CHOICE_B = "B"
	CHOICE_C = "C"
	CHOICE_D = "D"
	CHOICES = [
		(CHOICE_A, "A"),
		(CHOICE_B, "B"),
		(CHOICE_C, "C"),
		(CHOICE_D, "D"),
	]

	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
	text = models.TextField()
	choice_a = models.CharField(max_length=500)
	choice_b = models.CharField(max_length=500)
	choice_c = models.CharField(max_length=500)
	choice_d = models.CharField(max_length=500)
	correct_choice = models.CharField(max_length=1, choices=CHOICES)
	difficulty = models.PositiveSmallIntegerField(null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.text[:60]}..."

	def choices(self):
		"""Return a list of tuples (label, text) for choices in order A-D."""
		return [
			(self.CHOICE_A, self.choice_a),
			(self.CHOICE_B, self.choice_b),
			(self.CHOICE_C, self.choice_c),
			(self.CHOICE_D, self.choice_d),
		]


class Game(models.Model):
	STATUS_PENDING = "pending"
	STATUS_ACTIVE = "active"
	STATUS_FINISHED = "finished"
	STATUS_CHOICES = [
		(STATUS_PENDING, "Pending"),
		(STATUS_ACTIVE, "Active"),
		(STATUS_FINISHED, "Finished"),
	]

	player_name = models.CharField(max_length=150, blank=True)
	started_at = models.DateTimeField(default=timezone.now)
	finished_at = models.DateTimeField(null=True, blank=True)
	score = models.IntegerField(default=0)
	# optional preference used when selecting questions for this game
	difficulty_pref = models.PositiveSmallIntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"Game {self.pk} ({self.player_name or 'anon'})"

	def finish(self):
		self.status = self.STATUS_FINISHED
		self.finished_at = timezone.now()
		self.save()


class PlayerAnswer(models.Model):
	game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="answers")
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	selected_choice = models.CharField(max_length=1, choices=Question.CHOICES)
	correct = models.BooleanField()
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ["created_at"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"Game {self.game_id} - Q{self.question_id} -> {self.selected_choice} ({'OK' if self.correct else 'WRONG'})"

