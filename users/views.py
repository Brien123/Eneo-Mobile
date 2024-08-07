from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout as django_logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, EditProfileForm, ChangePhoneNumberForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Determine the backend
            backend = 'users.backends.PhoneNumberBackend'
            user.backend = backend

            # Log the user in
            login(request, user, backend=backend)
            # token, created = Token.objects.get_or_create(user=user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
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

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def change_phone_number(request):
    if request.method == 'POST':
        form = ChangePhoneNumberForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ChangePhoneNumberForm(instance=request.user)
    return render(request, 'change_phone_number.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
