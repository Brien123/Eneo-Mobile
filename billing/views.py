from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import Bill, Payment, Invoice
from users.models import User
from .forms import PaymentForm, BuyForm
from .utils import generate_invoice_pdf
from dotenv import load_dotenv
from django.http import HttpResponse
from campay.sdk import Client as CamPayClient
import os
from django.utils import timezone
import time
from .tasks import check_payment_status

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
            # user=request.user,
            # bill=bill,
            # number=number,
            # currency=currency,
            # amount=amount,
            # means=collect['operator'],
            # transaction_id=collect['reference']
#         )
#         return collect, 'Payment successful'

#     except Exception as e:
#         return None, str(e)

class InvoiceGenerationView(LoginRequiredMixin, View):
    def get(self, request, bill_id):
        bill = get_object_or_404(Bill, id=bill_id, user=request.user)
        invoice = generate_invoice_pdf(bill)
        return redirect('billing:bill_list')
    
class BuyView(LoginRequiredMixin, View):
    def get(self, request):
        form = BuyForm()
        return render(request, 'buy_view.html', {'form': form})

    def post(self, request):
        form = BuyForm(request.POST)
        if form.is_valid():
            unit = form.cleaned_data['unit']
            number = form.cleaned_data['number']
            eneo_id = form.cleaned_data['eneo_id']
            return self.buy(unit, number, eneo_id, request)
        return render(request, 'buy_view.html', {'form': form})

    def buy(self, unit, number, eneo_id, request):
        try:
            user = get_object_or_404(User, eneo_id=eneo_id)
        except User.DoesNotExist:
            return HttpResponse('User does not exist')

        amount = self.calculate_amount(unit)
        if not number.startswith('237'):
            number = '237' + number

        collect = campay.initCollect({
            "amount": amount,
            "currency": "XAF",
            "from": number,
            "description": f"Payment for {unit} kWh of electricity",
            "external_reference": "",  # Your reference for this transaction
        })

        if collect is None or 'operator' not in collect or 'reference' not in collect:
            # Log the collect response for debugging
            print("Collect response:", collect)
            return HttpResponse('Payment failed, please try again')
        else:
            bill = Bill.objects.create(
                user=request.user,
                amount=amount,
                due_date=timezone.now(),
                paid=True,
                created_at=timezone.now()
            )
            bill.save()
            
            reference = collect.get('reference', 'Unknown')
            payment = Payment.objects.create(
                user=request.user,
                bill=bill,
                number=number,
                currency='XAF',  # Assuming currency is XAF
                amount=amount,
                means=collect.get('operator', 'Unknown'),  # Use 'Unknown' if 'operator' is not present
                transaction_id=reference  # Use 'Unknown' if 'reference' is not present
            )
            payment.save()
            time.sleep(5)

            status = check_payment_status.delay(reference)

            return HttpResponse(f'Payment initiated, status will be updated shortly.')

    def calculate_amount(self, unit):
        if unit < 100:
            return 8 * unit
        else:
            return 9 * unit
        
