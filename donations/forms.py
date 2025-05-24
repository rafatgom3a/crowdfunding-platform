from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '0.01',
                'placeholder': 'Enter donation amount (e.g., 10.00)',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Donation amount must be greater than zero.")
        return amount