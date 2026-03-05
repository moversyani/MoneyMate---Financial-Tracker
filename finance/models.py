from django.db import models
from django.contrib.auth.models import User

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    label = models.CharField(max_length=100, default="Monthly Salary")

    def __str__(self):
        return f"{self.user.username}: £{self.amount}"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=[
        ('Housing', 'Housing'),
        ('Utilities', 'Utilities'),
        ('Transport', 'Transport'),
        ('Food', 'Food'),
        ('Entertainment', 'Entertainment'),
    ])

    def __str__(self):
        return f"{self.name}: £{self.amount}"