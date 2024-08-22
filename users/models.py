from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    address = models.CharField(max_length=50, blank=False, null=False)
    phone_number = models.CharField(max_length=15, unique=True, blank=False, null=False)
    role = models.CharField(max_length=15, choices=[('admin', 'Admin'), ('customer', 'Customer')], default='customer')
    eneo_id = models.CharField(max_length=15, blank=False, null=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email', 'address', 'eneo_id']

    def save(self, *args, **kwargs):
        if not self.phone_number.startswith('+237'):
            self.phone_number = '+237' + self.phone_number
        super(User, self).save(*args, **kwargs)
        
class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(max_length=2000)
    read_status = models.BooleanField(default=False)
    images = models.ImageField(upload_to='message_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.user.username}"
