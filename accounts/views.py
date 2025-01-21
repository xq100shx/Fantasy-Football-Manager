# authentication/views.py
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import SignupForm, LoginForm


def signup_view(request):
    form = SignupForm()
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'registration/signup.html', context={'form': form, 'title': 'Sign Up'})


def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'registration/login.html', context={'form': form, 'title': 'Login'})
