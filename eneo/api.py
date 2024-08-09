from ninja import NinjaAPI, Schema
from users import views
from users.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm, ChangePhoneNumberForm, EditProfileForm
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
from users.models import User
from django.db import transaction

api = NinjaAPI()

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
    
class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        token_obj = get_object_or_404(Token, key=token)
        return token_obj.user
    

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