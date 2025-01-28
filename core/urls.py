from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("team", views.team, name="team"),
    path("leaderboard", views.leaderboard, name="leaderboard"),
    path("about", views.about, name="about"),
]