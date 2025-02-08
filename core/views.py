from datetime import datetime, timedelta

from django.shortcuts import render
from core.models import Player, UpcomingMatch, League
from accounts.models import CustomUser as CustomUser

# Create your views here.

def index(request):
    today = datetime.today()
    monday = today - timedelta(days=today.weekday())
    # get all matches in the week
    matches = UpcomingMatch.objects.filter(date__range=[monday, monday + timedelta(days=6)])
    # group matches by league
    leagues = {}
    for match in matches:
        if match.league.name not in leagues:
            leagues[match.league.name] = []
        leagues[match.league.name].append(match.get_dictionary())
    return render(request, 'core/index.html', {
        'matches': leagues,
        'today': today.date(),
    })
def team(request):
    players = Player.objects.all()
    context = []
    for player in players:
        context.append(player.get_dictionary())
    #change player imaage to blob

    return render(request, 'core/team.html', {
        'players': context,
    })

def leaderboard(request):
    # We will show here the leaderboard
    users = CustomUser.objects.all()
    context = []
    for user in users:
        context.append(user.get_points())
    context = sorted(context, key=lambda k: k['score'], reverse=True)
    return render(request, 'core/leaderboard.html', {
        'users': context
    })

def about(request):
    return render(request, 'core/about.html', {})