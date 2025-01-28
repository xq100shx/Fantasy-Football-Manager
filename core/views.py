import datetime

from django.shortcuts import render
from core.models import Player, UpcomingMatch, League
from accounts.models import CustomUser as CustomUser

# Create your views here.

def index(request):
    today = datetime.date.today()
    # Get leagues names associated with id
    leagues = League.objects.all()
    league_dict = {league.id: league.name for league in leagues}

    # Get the distinct game weeks for each league
    game_weeks = UpcomingMatch.objects.values('game_week', 'league_id').distinct().order_by('league_id', 'game_week')

    # Prepare the data for rendering
    grouped_matches = {}
    for gw in game_weeks:
        league_id = gw['league_id']
        league_name = league_dict[league_id]
        game_week = gw['game_week']
        if league_id not in grouped_matches:
            grouped_matches[league_id] = {
                'league_name': league_name,
                'game_weeks': []
            }
        grouped_matches[league_id]['game_weeks'].append({
            'game_week': game_week,
            'fixtures': UpcomingMatch.objects.filter(
                league_id=league_id,
                game_week=game_week
            ).order_by('date')  # Sort by date
        })

    return render(request, 'core/index.html', {
        'grouped_matches': grouped_matches,
        'today': today
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