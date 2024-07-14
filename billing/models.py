from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import User

# Create your models here.
class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Bill {self.id} - {self.user.username}"

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    number = models.IntegerField(default=652592011)
    currency = models.CharField(default='XAF', max_length=12)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    means = models.CharField(max_length=12, default='MOMO')
    payment_date = models.DateTimeField(default=timezone.now)
    transaction_id = models.CharField(max_length=100)
    # reference = models.CharField()

    def __str__(self):
        return f"Payment {self.id} - {self.user.username}"

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill = models.OneToOneField(Bill, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    pdf = models.FileField(upload_to='invoices/')

    def __str__(self):
        return f"Invoice {self.id} - {self.user.username}"
