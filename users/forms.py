from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'address', 'role', 'eneo_id')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Phone number already exists.')
        return phone_number

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=50, label='Phone Number')
    password = forms.CharField(max_length=50, label='Password', strip=False, widget=forms.PasswordInput)

    def clean(self):
        phone_number = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if phone_number is not None and password:
            self.user_cache = authenticate(self.request, phone_number=phone_number, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def get_user(self):
        return self.user_cache

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)

class ChangePhoneNumberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number',)

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Phone number already exists.')
        return phone_number

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
