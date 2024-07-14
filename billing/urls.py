from django.urls import path
from .views import BillListView, PaymentProcessingView, InvoiceGenerationView

app_name = 'billing'

urlpatterns = [
    path('bills/', BillListView.as_view(), name='bill_list'),
    path('bills/pay/<int:bill_id>/', PaymentProcessingView.as_view(), name='payment_processing'),
    path('bills/invoice/<int:bill_id>/', InvoiceGenerationView.as_view(), name='generate_invoice'),
]
