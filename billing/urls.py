from django.urls import path
from .views import BillListView, PaymentProcessingView, InvoiceGenerationView, BuyView

app_name = 'billing'

urlpatterns = [
    path('bills/', BillListView.as_view(), name='bill_list'),
    path('bills/pay/<int:bill_id>/', PaymentProcessingView.as_view(), name='payment_processing'),
    path('bills/invoice/<int:bill_id>/', InvoiceGenerationView.as_view(), name='generate_invoice'),
    path('buy/', BuyView.as_view(), name='buy_view'),
]
