from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    address = models.CharField(max_length=50, blank=False, null=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    role = models.CharField(max_length=15, choices=[('admin', 'Admin'), ('customer', 'Customer')], default='customer')
    eneo_id = models.CharField(max_length=15, blank=False, null=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email', 'address', 'role', 'eneo_id']
