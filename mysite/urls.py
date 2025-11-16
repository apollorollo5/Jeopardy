from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("new-game/", views.new_game, name="new_game"),
    path("game/<int:game_id>/", views.game_board, name="game_board"),
    path("game/<int:game_id>/complete/", views.game_complete, name="game_complete"),
    path("api/game/<int:game_id>/state/", views.get_game_state_api, name="get_game_state"),
    path("api/question/<int:question_id>/", views.get_question, name="get_question"),
    path("api/game/<int:game_id>/answer/<int:question_id>/", views.submit_answer, name="submit_answer"),
]