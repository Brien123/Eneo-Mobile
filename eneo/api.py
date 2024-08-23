from ninja import NinjaAPI, Schema, File
from typing import Optional
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from users import views
from users.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm, ChangePhoneNumberForm, EditProfileForm
from billing.forms import *
from django.contrib.auth.backends import ModelBackend
from rest_framework.authtoken.models import Token
from users.backends import PhoneNumberBackend
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout as django_logout
from users.models import User
from ninja.security import django_auth, HttpBearer
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from users.models import *
from billing.models import *
from billing.tasks import *
from django.db import transaction
import os
from campay.sdk import Client as CamPayClient
from pydantic import BaseModel

api = NinjaAPI()
load_dotenv()

campay = CamPayClient({
    "app_username" : os.getenv('CAMPAY_USERNAME'),
    "app_password" : os.getenv('CAMPAY_PASSWORD'),
    "environment" : "DEV" #use "DEV" for demo mode or "PROD" for live mode
})

@api.get("/hello")
def hello(request):
    return "Hello world"

class RegisterSchema(Schema):
    username: str
    email: str
    phone_number: str
    address: str
    eneo_id: str
    password1: str
    password2: str
    role: str
    
class LoginSchema(Schema):
    phone_number: str
    password: str
    
class ChangeNameSchema(Schema):
    username: str

class ChangePhoneNumberSchema(Schema):
    phone_number: str
    
class ChangePasswordSchema(Schema):
    old_password: str
    new_password1: str
    new_password2: str
    
class PaymentSchema(Schema):
    unit: str
    number: str
    eneo_id: str
    
class MessageSchema(Schema):
    message: str
    read_status: Optional[bool] = None
    images: Optional[str] = None
    
class ReplyOutSchema(Schema):
    id: int
    admin: str
    reply: str
    created_at: str
    
class ReplyCreateSchema(Schema):
    message_id: int
    reply: str
    
class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        token_obj = get_object_or_404(Token, key=token)
        return token_obj.user

def calculate_amount(unit):
    if unit < 100:
        return 8 * unit
    else:
        return 9 * unit
    

@api.get("/get-csrf-token")
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})
    
    
@api.post("/register")
def register(request, payload: RegisterSchema):
    try:
        form_data = {
            'username': payload.username,
            'email': payload.email,
            'phone_number': payload.phone_number,
            'address': payload.address,
            'eneo_id': payload.eneo_id,
            'password1': payload.password1,
            'password2': payload.password2,
            'role': payload.role,
        }
        
        form = CustomUserCreationForm(form_data)
        
        if form.is_valid():
            user = form.save()
            backend = 'users.backends.PhoneNumberBackend' 
            user.backend = backend
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return {'message': 'User successfully created', 'token': token.key}
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@api.post('/login')
def login(request, payload: LoginSchema):
    try:
        form_data = {
            'username': payload.phone_number,
            'password': payload.password
        }
        if form_data['username'].startswith("+237"):
            form = CustomAuthenticationForm(request=request, data=form_data)
        else:
            form_data['username'] = "+237" + form_data['username']
            form = CustomAuthenticationForm(request=request, data=form_data)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return {'message': 'User successfully logged in', 'token': token.key}
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@api.post("/logout")
def logout(request):
    try:
        django_logout(request)
        return {'message': 'User successfully logged out'}
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

@api.post("/edit-username", auth=TokenAuth())
def edit_username(request, payload: ChangeNameSchema):
    try:
        user = request.auth  
        form = EditProfileForm(instance=user, data={'username': payload.username})

        if form.is_valid():
            user = form.save()
            return {'message': 'Username successfully updated', 'username': user.username}
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'message': False, "Error": (e)})
    
    
@api.post("/edit-number", auth=TokenAuth())
def edit_number(request, payload: ChangePhoneNumberSchema):
    try:
        user = request.auth
        form = ChangePhoneNumberForm(instance=user, data={'phone_number': payload.phone_number})
        
        if form.is_valid():
            user = form.save()
            return {'message': 'Phone number successfully updated', 'phone_number': user.phone_number}
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'message': False, "Error": (e)})    


@api.post('/edit-password', auth=TokenAuth())
def edit_password(request, payload: ChangePasswordSchema):
    try:
        user = request.auth
        form = CustomPasswordChangeForm(user, data={
            'old_password': payload.old_password,
            'new_password1': payload.new_password1,
            'new_password2': payload.new_password2
        })

        if form.is_valid():
            user = form.save()
            return JsonResponse({'success': True, 'message': 'Password changed successfully', 'password': user.password})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    
@api.get('/profile', auth=TokenAuth())
def profile(request):
    try:
        user = request.auth
        name = user.username
        number = user.phone_number
        email = user.email

        return JsonResponse({'name': name, 'number': number, 'email': email})
    except Exception as e:
        return JsonResponse({'message': False, 'errors': (e)})
    

@api.get('/energy-history', auth=TokenAuth())
def energy(request):
    try:
        user = request.auth
        units = Power.objects.filter(user=user).values('unit')
        payments = Payment.objects.filter(user=user).values('amount')
        
        return JsonResponse({
            'name': user.username,
            'units': list(units),
            'payments': list(payments)
        })
    except Exception as e:
        return JsonResponse({'message': 'Failed to retrieve energy history', 'errors': str(e)}, status=400)
    
    
@api.post('/create-message', auth=TokenAuth())
def support(request):
    user = request.auth 
    message_text = request.POST.get('message')
    read_status = request.POST.get('read_status') == 'true'
    image_file = request.FILES.get('images')

    try:
        message = Messages.objects.create(
            user=user,
            message=message_text,
            read_status=read_status,
            images=image_file 
        )
        return {"success": True, "message": "Message created successfully", "id": message.id}
    except Exception as e:
        return {"success": False, "error": str(e)}
   
    
@api.get('/messages', auth=TokenAuth())
def get_messages(request):
    user = request.auth
    messages = Messages.objects.filter(user=user)
    return [
        {
            "id": message.id,
            "user": message.user.username,
            "message": message.message,
            "read_status": message.read_status,
            "images": message.images.url if message.images else None,
            "created_at": message.created_at.isoformat()
        }
        for message in messages
    ]
    
    
@api.post('/reply-message', auth=TokenAuth())
def reply_message(request, payload: ReplyCreateSchema):
    user = request.auth
    try:
        message = Messages.objects.get(id=payload.message_id)
        reply = Reply.objects.create(
            message=message,
            admin=user,
            reply=payload.reply
        )
        return {"success": True, "id": reply.id}
    except Message.DoesNotExist:
        return {"success": False, "error": "Message not found"}
 
    
@api.get('/chat', auth=TokenAuth())
def get_chat(request):
    user = request.auth
    messages = Messages.objects.filter(user=user)
    response = []
    
    for message in messages:
        replies = Reply.objects.filter(message=message)
        message_with_replies = {
            "id": message.id,
            "user": message.user.username,
            "message": message.message,
            "read_status": message.read_status,
            "images": message.images.url if message.images else None,
            "created_at": message.created_at.isoformat(),
            "replies": [
                {
                    "id": reply.id,
                    "admin": reply.admin.username,
                    "reply": reply.reply,
                    "created_at": reply.created_at.isoformat()
                }
                for reply in replies
            ]
        }
        response.append(message_with_replies)
    
    return response
         
    
@api.post('/buy', auth=TokenAuth())
def buy(request, payload: PaymentSchema):
    try:
        user = request.auth
        form = BuyForm(data={'unit': payload.unit, 'number': payload.number, 'eneo_id': payload.eneo_id})
        
        if not form.is_valid():
            return JsonResponse({"message": "Invalid form data"}, status=400)

        number = payload.number
        if not number.startswith('237'):
            number = '237' + number
            
        unit = int(payload.unit)
        amount = calculate_amount(unit)
        
        # Initiate payment
        collect = campay.initCollect({
            "amount": amount,
            "currency": "XAF",
            "from": number,
            "description": f"Payment for {unit} kWh of electricity",
            "external_reference": "",
        })
        
        if collect is None or 'operator' not in collect or 'reference' not in collect:
            print("Collect response:", collect)
            return JsonResponse({"message": "Payment failed, please try again"}, status=500)
        
        bill = Bill.objects.create(
            user=user,
            amount=amount,
            due_date=timezone.now(),
            paid=False,
            created_at=timezone.now()
        )
        bill.save()
        bill_id = bill.id
        
        reference = collect.get('reference', 'Unknown')
        payment = Payment.objects.create(
            user=user,
            bill=bill,
            number=number,
            currency='XAF', 
            amount=amount,
            means=collect.get('operator', 'Unknown'),
            transaction_id=reference  
        )
        payment.save()
        time.sleep(5)
        check_payment_status.delay(reference, bill_id, unit)  
        return JsonResponse({"message": "Payment initiated, status will be updated shortly."})

        
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'message': 'Payment failed'}, status=500)
