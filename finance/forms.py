# forms.py — MoneyMate form definitions

from django import forms
from .models import Expense, Income


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        # company is now included so users can log who their bill is with
        fields = ['name', 'company', 'amount', 'category']
        widgets = {
            'name':     forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Car Insurance'
            }),
            'company':  forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Admiral, Vodafone, Severn Trent'
            }),
            'amount':   forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model  = Income
        fields = ['source', 'amount']
        widgets = {
            'source': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Monthly Salary'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00'
            }),
        }