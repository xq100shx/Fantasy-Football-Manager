import datetime

from django.shortcuts import render
from django.http import HttpResponse

from core.models import Player, UpcomingMatch


# Create your views here.
def index(request):
    # We will show here upcoming matches for today's date game_week
    # Check which game_week is today
    gw = UpcomingMatch.objects.filter(date=datetime.date.today()).first().game_week
    # Get all matches for that game_week
    matches = UpcomingMatch.objects.filter(game_week=gw).order_by('date')

    # Group matches by date
    grouped_matches = {}
    for match in matches:
        match_date = match.date.strftime('%Y-%m-%d')
        if match_date not in grouped_matches:
            grouped_matches[match_date] = []
        grouped_matches[match_date].append(match.get_dictionary())

    return render(request, 'core/index.html', {
        'game_week': gw,
        'grouped_matches': grouped_matches
    })

def team(request):
    players = Player.objects.all()
    context = []
    for player in players:
        context.append(player.get_dictionary())
    #change player imaage to blob

    return render(request, 'core/team.html', {
        'players': context
    })

def view_leaderboard(request):
    return HttpResponse("Hello, world. You're at the core view_leaderboard.")

