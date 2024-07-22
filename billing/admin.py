from django.contrib import admin
from .models import Bill, Payment, Invoice
# Register your models here.

admin.site.register(Bill)
admin.site.register(Payment)
admin.site.register(Invoice)