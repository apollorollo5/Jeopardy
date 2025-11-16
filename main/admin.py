from django.contrib import admin
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = ("text", "category", "difficulty", "created_at")
	list_filter = ("category", "difficulty")
	search_fields = ("text",)


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
	list_display = ("id", "player_name", "status", "score", "started_at", "finished_at")
	list_filter = ("status",)
	search_fields = ("player_name",)


@admin.register(models.PlayerAnswer)
class PlayerAnswerAdmin(admin.ModelAdmin):
	list_display = ("game", "question", "selected_choice", "correct", "created_at")
	list_filter = ("correct",)
	search_fields = ("question__text",)
