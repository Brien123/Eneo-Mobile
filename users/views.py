from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout as django_logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')  
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'home.html')

def logout(request):
    django_logout(request)
    return redirect('login')
