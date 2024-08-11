from django.urls import path
from .views import *

app_name = 'notifications'
urlpatterns = [
    path('notifications/', notification_list, name='notification_list'),
    path('notifications/mark-as-read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
]
