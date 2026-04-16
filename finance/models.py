# models.py — MoneyMate data models

from django.db import models
from django.contrib.auth.models import User


# Stores income sources — linked to the logged-in user
class Income(models.Model):
    # ForeignKey ties each record to a user — CASCADE deletes records if user is deleted
    user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    source     = models.CharField(max_length=100)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - £{self.amount}"


# Stores monthly bills — linked to the logged-in user
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
        ('OTHERS',        'Others / One-off Payments'),
    ]

    # ForeignKey ties each bill to a user — CASCADE deletes records if user is deleted
    user       = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name       = models.CharField(max_length=100)
    company    = models.CharField(max_length=100, blank=True, default='')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    category   = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHERS')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company}) - £{self.amount}" if self.company else f"{self.name} - £{self.amount}"