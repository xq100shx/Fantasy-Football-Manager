from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'core/index.html')

def create_team(request):
    return HttpResponse("Hello, world. You're at the core create_team.")

def edit_team(request):
    return HttpResponse("Hello, world. You're at the core edit_team.")

def view_leaderboard(request):
    return HttpResponse("Hello, world. You're at the core view_leaderboard.")

def view_team(request):
    return HttpResponse("Hello, world. You're at the core view_team.")

def profile(request):
    return HttpResponse("Hello, world. You're at the core profile.")
