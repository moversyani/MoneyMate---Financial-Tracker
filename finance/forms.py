from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        # We want the user to fill in these three things
        fields = ['name', 'amount', 'category']
        
        # This adds CSS classes so the form looks nice with our styling
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Netflix'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }