from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("team", views.team, name="team"),
    path("view_leaderboard", views.leaderboard, name="view_leaderboard"),
    path("about", views.about, name="about"),
]