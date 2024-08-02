from celery import shared_task
from .models import Payment
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
def check_payment_status(reference):
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
            break  # Exit the loop if we get a success status
        
        attempt += 1
        time.sleep(5)  # Delay between attempts to avoid spamming the API

    if status is None:
        print(f'Payment status could not be verified for reference {reference}.')
    return status
