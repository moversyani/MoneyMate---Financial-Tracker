# models.py — MoneyMate data models

from django.db import models


# Stores where income comes from e.g. Monthly Salary, Freelance
class Income(models.Model):
    source     = models.CharField(max_length=100)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - £{self.amount}"


# Stores monthly bills with category, optional company name, and amount
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
        ('MOBILE',        'Mobile / Phone'),   # new: needed for mobile deal matching
        ('OTHERS',        'Others / One-off Payments'),
    ]

    name       = models.CharField(max_length=100)
    # Company field — optional, e.g. "Admiral", "Vodafone", "Severn Trent"
    company    = models.CharField(max_length=100, blank=True, default='')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    category   = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHERS')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company}) - £{self.amount}" if self.company else f"{self.name} - £{self.amount}"