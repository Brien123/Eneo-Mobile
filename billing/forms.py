from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['number', 'amount']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
        }

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['number'].label = "Phone Number"
        self.fields['amount'].label = "Amount to Pay"


class BuyForm(forms.Form):
    unit = forms.IntegerField(label='Units of Electricity')
    number = forms.CharField(label='Phone Number')
    eneo_id = forms.CharField(label='Eneo ID')