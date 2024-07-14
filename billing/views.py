from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Bill, Payment, Invoice
from .forms import PaymentForm
from .utils import generate_invoice_pdf
from dotenv import load_dotenv
from campay.sdk import Client as CamPayClient
import os

load_dotenv()

campay = CamPayClient({
    "app_username" : os.getenv('CAMPAY_USERNAME'),
    "app_password" : os.getenv('CAMPAY_PASSWORD'),
    "environment" : "DEV" #use "DEV" for demo mode or "PROD" for live mode
})

# Create your views here
class BillListView(LoginRequiredMixin, View):
    def get(self, request):
        bills = Bill.objects.filter(user=request.user)
        return render(request, 'bill_list.html', {'bills': bills})

class PaymentProcessingView(LoginRequiredMixin, View):
    def get(self, request, bill_id):
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        form = PaymentForm()
        return render(request, 'payment_form.html', {'form': form, 'bill': bill})

    def post(self, request, bill_id):
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            # Collect payment details
            collect = campay.initCollect({
                "amount": payment.amount,
                "currency": "XAF",
                "from": payment.number,
                "description": f"Payment for Bill {bill.id}",
                "external_reference": "",  # Your reference for this transaction
            })

            if collect is None:
                return render(request, 'payment_form.html', {'form': form, 'bill': bill, 'error': 'Payment failed, please try again.'})
            else:
                payment.user = request.user
                payment.bill = bill
                payment.currency = "XAF"
                payment.means = collect['operator']
                payment.transaction_id = collect['reference']
                payment.save()
                
                bill.paid = True
                bill.save()
                
                return redirect('billing:bill_list')
        return render(request, 'payment_form.html', {'form': form, 'bill': bill})


# def collect_payment(amount, currency, number, description, request, bill):
#     try:
#         collect = Campay().initCollect({
#             "amount": amount,  # The amount you want to collect
#             "currency": currency,
#             "from": number,  # Phone number to request amount from. Must include country code
#             "description": description,
#             "external_reference": "",  # Reference from the system initiating the transaction.
#         })
        
#         if collect is None:
#             return None, 'Payment failed, try again'
        
#         # Saving the payment details
#         payment = Payment.objects.create(
#             user=request.user,
#             bill=bill,
#             number=number,
#             currency=currency,
#             amount=amount,
#             means=collect['operator'],
#             transaction_id=collect['reference']
#         )
#         return collect, 'Payment successful'

#     except Exception as e:
#         return None, str(e)

class InvoiceGenerationView(LoginRequiredMixin, View):
    def get(self, request, bill_id):
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        invoice = generate_invoice_pdf(bill)
        return redirect('billing:bill_list')
    
