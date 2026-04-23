# models.py — MoneyMate data models

from django.db import models
from django.contrib.auth.models import User


# Stores income sources linked to the logged-in user
class Income(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    source     = models.CharField(max_length=100)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - £{self.amount}"


# Stores monthly bills linked to the logged-in user
class Expense(models.Model):

    CATEGORY_CHOICES = [
        ('MORTGAGE',      'Mortgage'),
        ('INSURANCE',     'Insurances (Car/Life/House)'),
        ('UTILITIES',     'Utilities (Gas/Water/Elec)'),
        ('SUBSCRIPTIONS', 'Subscriptions (Netflix/Spotify)'),
        ('GROCERIES',     'Groceries'),
        ('DEBTS',         'Debts'),
        ('FUEL',          'Fuel / Transport'),
        ('LOANS',         'Loans / Car Finance'),
        ('MOBILE',        'Mobile / Phone'),
        ('SAVINGS',       'Savings'),
        ('INVESTMENTS',   'Investments'),
        ('OTHERS',        'Others / One-off Payments'),
    ]

    # Monthly or annual — annual amounts are divided by 12 in monthly_amount()
    FREQUENCY_CHOICES = [
        ('MONTHLY',  'Monthly'),
        ('ANNUALLY', 'Annually'),
    ]

    # Fixed = same amount every month (mortgage, insurance etc.)
    # Variable = changes month to month (credit card, groceries etc.)
    BILL_TYPE_CHOICES = [
        ('FIXED',    'Fixed'),
        ('VARIABLE', 'Variable'),
    ]

    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name            = models.CharField(max_length=100)
    company         = models.CharField(max_length=100, blank=True, default='')
    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHERS')
    frequency       = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='MONTHLY')
    # bill_type defaults to FIXED — user can change to VARIABLE for fluctuating costs
    bill_type       = models.CharField(max_length=10, choices=BILL_TYPE_CHOICES, default='FIXED')

    # Advanced optional fields — blank=True so existing bills aren't broken
    customer_number = models.CharField(max_length=100, blank=True, default='')
    tariff_details  = models.CharField(max_length=200, blank=True, default='')
    start_date      = models.DateField(null=True, blank=True)
    end_date        = models.DateField(null=True, blank=True)

    date_added      = models.DateTimeField(auto_now_add=True)

    def monthly_amount(self):
        # Normalises annual bills to monthly so totals are always comparable
        if self.frequency == 'ANNUALLY':
            return self.amount / 12
        return self.amount

    def __str__(self):
        return f"{self.name} ({self.company}) - £{self.amount}" if self.company else f"{self.name} - £{self.amount}"