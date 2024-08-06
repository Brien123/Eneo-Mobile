from celery import shared_task
from .models import Payment, Bill
from users.models import User
import time
from campay.sdk import Client as CamPayClient
from dotenv import load_dotenv
import os

load_dotenv()

campay = CamPayClient({
    "app_username" : os.getenv('CAMPAY_USERNAME'),
    "app_password" : os.getenv('CAMPAY_PASSWORD'),
    "environment" : "DEV" #use "DEV" for demo mode or "PROD" for live mode
})

@shared_task
def check_payment_status(reference, bill_id):
    max_attempts = 5
    attempt = 0
    status = None

    while attempt < max_attempts and status != 'SUCCESSFUL':
        campay_status = campay.get_transaction_status({
            "reference": reference,
        })

        status = campay_status.get('status')
        if status == 'SUCCESSFUL':
            Payment.objects.filter(transaction_id=reference).update(paid=status)
            Bill.objects.filter(id=bill_id).update(paid=True)
            break  # Exit the loop if we get a success status
        
        attempt += 1
        time.sleep(5)

    if status is None:
        print(f'Payment status could not be verified for reference {reference}.')
    return status

@shared_task
def check_unpaid_bills(user_id):
    try:
        user = User.objects.filter(id=user_id)
        unpaid_bills = Bill.objects.filter(paid=0, user=user)
        return unpaid_bills.exists() 
    except Exception as e:
        return f"error: {e}"
    
