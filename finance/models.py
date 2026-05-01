# models.py — MoneyMate data models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Stores income sources linked to the logged-in user
class Income(models.Model):
    user         = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    source       = models.CharField(max_length=100)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    # month/year determine which month this income record belongs to
    month        = models.IntegerField(default=1)
    year         = models.IntegerField(default=2026)
    # is_recurring: True = rolls over automatically, False = one-off income only
    is_recurring = models.BooleanField(default=True)
    date_added   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - £{self.amount} ({self.month}/{self.year})"


# Stores bills linked to the logged-in user
class Expense(models.Model):

    CATEGORY_CHOICES = [
        ('MORTGAGE',      'Mortgage'),
        ('INSURANCE',     'Insurance'),
        ('UTILITIES',     'Utilities (Gas/Water/Elec)'),
        ('SUBSCRIPTIONS', 'Subscriptions'),
        ('GROCERIES',     'Groceries'),
        ('DEBTS',         'Debts'),
        ('FUEL',          'Fuel / Transport'),
        ('LOANS',         'Loans / Car Finance'),
        ('MOBILE',        'Mobile / Phone'),
        ('SAVINGS',       'Savings'),
        ('INVESTMENTS',   'Investments'),
        ('OTHERS',        'Others / One-off Payments'),
    ]

    # Sub-types per category — only relevant ones shown based on category selected
    SUB_TYPE_CHOICES = [
        # Insurance sub-types
        ('INS_CAR',        'Car Insurance'),
        ('INS_HOME',       'Home Insurance'),
        ('INS_LIFE',       'Life Insurance'),
        ('INS_HEALTH',     'Health Insurance'),
        ('INS_TRAVEL',     'Travel Insurance'),
        ('INS_PET',        'Pet Insurance'),
        ('INS_OTHER',      'Other Insurance'),
        # Loans sub-types
        ('LOAN_PERSONAL',  'Personal Loan'),
        ('LOAN_CAR',       'Car Finance'),
        ('LOAN_STUDENT',   'Student Loan'),
        ('LOAN_PAYDAY',    'Payday Loan'),
        ('LOAN_OTHER',     'Other Loan'),
        # Debts sub-types
        ('DEBT_CREDIT',    'Credit Card'),
        ('DEBT_OVERDRAFT', 'Overdraft'),
        ('DEBT_BNPL',      'Buy Now Pay Later'),
        ('DEBT_OTHER',     'Other Debt'),
        # Subscriptions sub-types
        ('SUB_STREAMING',  'Streaming (Netflix/Disney)'),
        ('SUB_MUSIC',      'Music (Spotify/Apple)'),
        ('SUB_GAMING',     'Gaming'),
        ('SUB_SOFTWARE',   'Software/Apps'),
        ('SUB_GYM',        'Gym / Fitness'),
        ('SUB_OTHER',      'Other Subscription'),
        # Utilities sub-types
        ('UTIL_GAS',       'Gas'),
        ('UTIL_ELECTRIC',  'Electricity'),
        ('UTIL_WATER',     'Water'),
        ('UTIL_COUNCIL',   'Council Tax'),
        ('UTIL_BROADBAND', 'Broadband'),
        ('UTIL_OTHER',     'Other Utility'),
    ]

    FREQUENCY_CHOICES = [
        ('MONTHLY',  'Monthly'),
        ('ANNUALLY', 'Annually'),
        ('ONE_OFF',  'One-off'),  # full amount counted this month, does not roll over
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
    # sub_type narrows down the category — blank=True since not all categories have sub-types
    sub_type        = models.CharField(max_length=20, choices=SUB_TYPE_CHOICES, blank=True, default='')
    frequency       = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='MONTHLY')
    bill_type       = models.CharField(max_length=10, choices=BILL_TYPE_CHOICES, default='FIXED')
    # month/year determine which month this bill belongs to
    month           = models.IntegerField(default=1)
    year            = models.IntegerField(default=2026)
    customer_number = models.CharField(max_length=100, blank=True, default='')
    tariff_details  = models.CharField(max_length=200, blank=True, default='')
    start_date      = models.DateField(null=True, blank=True)
    end_date        = models.DateField(null=True, blank=True)
    date_added      = models.DateTimeField(auto_now_add=True)

    def monthly_amount(self):
        # Annual bills divided by 12 — monthly and one-off return the full amount
        if self.frequency == 'ANNUALLY':
            return self.amount / 12
        return self.amount

    def is_recurring(self):
        # Fixed monthly/annual bills roll over — one-off and variable do not
        return self.frequency in ('MONTHLY', 'ANNUALLY') and self.bill_type == 'FIXED'

    def __str__(self):
        return f"{self.name} ({self.company}) - £{self.amount}" if self.company else f"{self.name} - £{self.amount}"


# Stores savings goals linked to the logged-in user
class SavingsGoal(models.Model):
    user                 = models.ForeignKey(User, on_delete=models.CASCADE)
    name                 = models.CharField(max_length=100)
    target_amount        = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # monthly_contribution auto-suggested from disposable income but user can override
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created         = models.DateTimeField(auto_now_add=True)

    def progress_percent(self):
        # Returns % complete, capped at 100
        if self.target_amount <= 0:
            return 0
        return min(100, round((self.current_amount / self.target_amount) * 100, 1))

    def months_remaining(self):
        # How many months until goal is reached at the current contribution rate
        remaining = self.target_amount - self.current_amount
        if self.monthly_contribution <= 0 or remaining <= 0:
            return None
        return round(remaining / self.monthly_contribution)

    def __str__(self):
        return f"{self.name} — £{self.current_amount}/£{self.target_amount}"