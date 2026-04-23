# forms.py — MoneyMate form definitions

from django import forms
from .models import Expense, Income


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        # Category first — sets context before the user fills anything else
        fields = [
            'category', 'name', 'company', 'amount', 'frequency', 'bill_type',
            'customer_number', 'tariff_details', 'start_date', 'end_date',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Car Insurance',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Admiral, Vodafone, Severn Trent',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
            }),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            # Fixed or Variable — shown alongside frequency in the form
            'bill_type': forms.Select(attrs={'class': 'form-control'}),
            'customer_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 123456789',
            }),
            'tariff_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Standard Variable, Gold Policy',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model  = Income
        fields = ['source', 'amount']
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
        }