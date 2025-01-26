from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("team", views.team, name="team"),
    # path("edit_team", views.edit_team, name="edit_team"),
    path("view_leaderboard", views.leaderboard, name="view_leaderboard"),
    # path("view_team", views.view_team, name="view_team"),
    # path("profile", views.profile, name="profile"),

]