from django.urls import path
from .views import register, login_view, home, profile, logout

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    # path('', home, name='home'),
    path('profile/', profile, name='profile'),
    path('logout/', logout, name='logout'),
    # path('logout/', logout_view, name='logout'),
]
