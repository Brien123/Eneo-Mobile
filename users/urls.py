from django.urls import path
from .views import register, login_view, home, profile, logout, edit_profile, change_password, change_phone_number, home

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    # path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('home/', home, name='home'),
    path('logout/', logout, name='logout'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('change_phone_number/', change_phone_number, name='change_phone_number'),
    path('change_password/', change_password, name='change_password'),
    # path('logout/', logout_view, name='logout'),
]
