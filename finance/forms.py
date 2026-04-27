# forms.py — MoneyMate form definitions

from django import forms
from .models import Expense, Income, SavingsGoal


class ExpenseForm(forms.ModelForm):
    class Meta:
        model  = Expense
        fields = [
            'category', 'name', 'company', 'amount', 'frequency', 'bill_type',
            'customer_number', 'tariff_details', 'start_date', 'end_date',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Car Insurance'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Admiral, Vodafone'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'bill_type': forms.Select(attrs={'class': 'form-control'}),
            'customer_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 123456789'}),
            'tariff_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Standard Variable'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model  = Income
        fields = ['source', 'amount']
        widgets = {
            'source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Monthly Salary'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
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