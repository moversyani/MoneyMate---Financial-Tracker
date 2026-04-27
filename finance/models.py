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

    FREQUENCY_CHOICES = [
        ('MONTHLY',  'Monthly'),
        ('ANNUALLY', 'Annually'),
    ]

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
    bill_type       = models.CharField(max_length=10, choices=BILL_TYPE_CHOICES, default='FIXED')
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


# Stores savings goals linked to the logged-in user
class SavingsGoal(models.Model):
    user               = models.ForeignKey(User, on_delete=models.CASCADE)
    name               = models.CharField(max_length=100)           # e.g. "Holiday to Ibiza"
    target_amount      = models.DecimalField(max_digits=10, decimal_places=2)  # total to save
    current_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # saved so far
    # monthly_contribution is auto-suggested from disposable income but user can override
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created       = models.DateTimeField(auto_now_add=True)

    def progress_percent(self):
        # Returns how far along the goal is as a percentage (capped at 100)
        if self.target_amount <= 0:
            return 0
        return min(100, round((self.current_amount / self.target_amount) * 100, 1))

    def months_remaining(self):
        # Calculates how many months until the goal is reached based on monthly contribution
        remaining = self.target_amount - self.current_amount
        if self.monthly_contribution <= 0 or remaining <= 0:
            return None
        return round(remaining / self.monthly_contribution)

    def __str__(self):
        return f"{self.name} — £{self.current_amount}/£{self.target_amount}"