from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone_number', 'address', 'eneo_id')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'address': forms.TextInput(attrs={'placeholder': 'Address'}),
            'eneo_id': forms.TextInput(attrs={'placeholder': 'ENEO ID'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label = ''  # Remove the label
            field.help_text = ''  # Remove any help text
            field.widget.attrs.update({'class': 'form-control'})

        # Add placeholders for password fields
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

        # Specifically remove help text for password fields
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('Phone number already exists.')
        return phone_number

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=50,
        label='',
        widget=forms.TextInput(attrs={'placeholder': "Enter Phone Number", 'class': 'form-control'})
    )
    password = forms.CharField(
        max_length=50,
        label='',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': "Enter Password", 'class': 'form-control'})
    )

    def clean(self):
        phone_number = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not phone_number.startswith('+237'):
            phone_number = '+237' + phone_number
            
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
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter new username', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = ''

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username

class ChangePhoneNumberForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('phone_number',)
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter new phone number',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ChangePhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].label = ''  # Remove the label

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
