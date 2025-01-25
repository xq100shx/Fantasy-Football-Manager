from django.shortcuts import render
from django.http import HttpResponse

from core.models import Player


# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def team(request):
    players = Player.objects.all()
    context = []
    for player in players:
        context.append(player.get_dictionary())
    #change player imaage to blob

    return render(request, 'core/team.html', {
        'players': context
    })

# def edit_team(request):
#     return HttpResponse("Hello, world. You're at the core edit_team.")

def view_leaderboard(request):
    return HttpResponse("Hello, world. You're at the core view_leaderboard.")

# def view_team(request):
#     return HttpResponse("Hello, world. You're at the core view_team.")

# def profile(request):
#     return HttpResponse("Hello, world. You're at the core profile.")
