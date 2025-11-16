from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.start_game, name="start"),
    path("game/<int:game_id>/question/", views.question_view, name="question"),
    path("game/<int:game_id>/answer/", views.answer_view, name="answer"),
    path("game/<int:game_id>/score/", views.score_view, name="score"),
]
