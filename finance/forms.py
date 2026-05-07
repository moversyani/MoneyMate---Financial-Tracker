# forms.py — MoneyMate form definitions

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Income, SavingsGoal


# Maps each category to its relevant sub-type choices
# Used by JS in the template to show/hide the sub_type dropdown dynamically
CATEGORY_SUB_TYPES = {
    'INSURANCE':     [
        ('', '-- Select type --'),
        ('INS_CAR',    'Car Insurance'),
        ('INS_HOME',   'Home Insurance'),
        ('INS_LIFE',   'Life Insurance'),
        ('INS_HEALTH', 'Health Insurance'),
        ('INS_TRAVEL', 'Travel Insurance'),
        ('INS_PET',    'Pet Insurance'),
        ('INS_OTHER',  'Other Insurance'),
    ],
    'LOANS':         [
        ('', '-- Select type --'),
        ('LOAN_PERSONAL', 'Personal Loan'),
        ('LOAN_CAR',      'Car Finance'),
        ('LOAN_STUDENT',  'Student Loan'),
        ('LOAN_PAYDAY',   'Payday Loan'),
        ('LOAN_OTHER',    'Other Loan'),
    ],
    'DEBTS':         [
        ('', '-- Select type --'),
        ('DEBT_CREDIT',    'Credit Card'),
        ('DEBT_OVERDRAFT', 'Overdraft'),
        ('DEBT_BNPL',      'Buy Now Pay Later'),
        ('DEBT_OTHER',     'Other Debt'),
    ],
    'SUBSCRIPTIONS': [
        ('', '-- Select type --'),
        ('SUB_STREAMING', 'Streaming (Netflix/Disney)'),
        ('SUB_MUSIC',     'Music (Spotify/Apple)'),
        ('SUB_GAMING',    'Gaming'),
        ('SUB_SOFTWARE',  'Software/Apps'),
        ('SUB_GYM',       'Gym / Fitness'),
        ('SUB_OTHER',     'Other Subscription'),
    ],
    'UTILITIES':     [
        ('', '-- Select type --'),
        ('UTIL_GAS',       'Gas'),
        ('UTIL_ELECTRIC',  'Electricity'),
        ('UTIL_WATER',     'Water'),
        ('UTIL_COUNCIL',   'Council Tax'),
        ('UTIL_BROADBAND', 'Broadband'),
        ('UTIL_OTHER',     'Other Utility'),
    ],
}


# Extends Django's built-in UserCreationForm to add a required email field
class RegisterForm(UserCreationForm):
    # Email is required — used for verification
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
        }),
        help_text='A verification link will be sent to this address.',
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Style the password fields to match the rest of the app
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        })

    def clean_email(self):
        # Prevent duplicate email registrations
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        # Category and sub_type first — sets context before other fields
        fields = [
            'category', 'sub_type', 'name', 'company', 'amount', 'frequency',
            'bill_type', 'customer_number', 'tariff_details', 'start_date', 'end_date',
        ]
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
                # onchange triggers JS to show/hide the sub_type row
                'onchange': 'updateSubType(this.value)',
            }),
            # sub_type is hidden by default — JS shows it for relevant categories
            'sub_type':        forms.Select(attrs={'class': 'form-control'}),
            'name':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Car Insurance'}),
            'company':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Admiral, Vodafone'}),
            'amount':          forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'frequency':       forms.Select(attrs={'class': 'form-control'}),
            'bill_type':       forms.Select(attrs={'class': 'form-control'}),
            'customer_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 123456789'}),
            'tariff_details':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Standard Variable'}),
            'start_date':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':        forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model  = Income
        fields = ['source', 'amount', 'is_recurring']
        widgets = {
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Monthly Salary',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            # Checkbox: ticked = rolls over each month, unticked = one-off income
            'is_recurring': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_recurring': 'Recurring income (rolls over each month)',
        }


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model  = SavingsGoal
        fields = ['name', 'target_amount', 'current_amount', 'monthly_contribution']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Holiday to Ibiza, New Car, Emergency Fund',
            }),
            'target_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'current_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            # monthly_contribution is pre-filled in the view with the suggested amount
            'monthly_contribution': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
        }