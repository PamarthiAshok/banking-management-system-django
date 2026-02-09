from django import forms
from .models import BankAccount


class AccountRegistrationForm(forms.ModelForm):

    class Meta:
        model = BankAccount
        fields = [
            'full_name',
            'date_of_birth',
            'phone_number',
            'email',
            'aadhaar_number',
            'pan_number',
            'profile_photo',
            'gender',
            'address',
            'state',
            'nominee_name',
            'nominee_phone',
            'nominee_relationship',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
