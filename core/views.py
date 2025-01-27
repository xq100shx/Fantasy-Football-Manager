import datetime

from django.shortcuts import render
from core.models import Player, UpcomingMatch, League
from accounts.models import CustomUser as CustomUser
from django.db.models import Min, Max

# Create your views here.

def index(request):
    # Get today's date
    today = datetime.date.today()

    # Get leagues names associated with id
    leagues = League.objects.all()
    league_dict = {league.id: league.name for league in leagues}

    # Get the distinct game weeks with min and max dates for each league
    game_weeks = UpcomingMatch.objects.filter(date__lte=today).values('game_week', 'home_team__league').annotate(
        min_date=Min('date'),
        max_date=Max('date')
    ).order_by('game_week', 'home_team__league')

    # Prepare the data for rendering
    grouped_matches = {}
    for gw in game_weeks:
        league_id = gw['home_team__league']
        league_name = league_dict[league_id]
        game_week = gw['game_week']
        min_date = gw['min_date']
        max_date = gw['max_date']
        if league_id not in grouped_matches:
            grouped_matches[league_id] = {
                'league_name': league_name,
                'game_weeks': []
            }
        grouped_matches[league_id]['game_weeks'].append({
            'game_week': game_week,
            'min_date': min_date,
            'max_date': max_date,
            'fixtures': UpcomingMatch.objects.filter(
                home_team__league_id=league_id,
                game_week=game_week,
                date__range=(min_date, max_date)
            ).order_by('date')  # Sortowanie po dacie
        })

    return render(request, 'core/index.html', {
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

