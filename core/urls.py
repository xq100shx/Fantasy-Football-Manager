from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create_team", views.create_team, name="create_team"),
    path("edit_team", views.edit_team, name="edit_team"),
    path("view_leaderboard", views.view_leaderboard, name="view_leaderboard"),
    path("view_team", views.view_team, name="view_team"),
    path("profile", views.profile, name="profile"),

]