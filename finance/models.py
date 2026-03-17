from django.db import models

# Income Model: Stores where the money comes from
class Income(models.Model):
    source = models.CharField(max_length=100) # e.g., Salary, Side Hustle
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - £{self.amount}"

# Expense Model: Stores where the money goes (with your refined categories!)
class Expense(models.Model):
    # Standardized categories for better data analysis
    CATEGORY_CHOICES = [
        ('MORTGAGE', 'Mortgage'),
        ('INSURANCE', 'Insurances (Car/Life/House)'),
        ('UTILITIES', 'Utilities (Gas/Water/Elec)'),
        ('SUBSCRIPTIONS', 'Subscriptions (Netflix/Spotify)'),
        ('GROCERIES', 'Groceries'),
        ('DEBTS', 'Debts'),
        ('FUEL', 'Fuel/Transport'),
        ('LOANS', 'Loans / Car Finance'),
        ('OTHERS', 'Others / One-off Payments'),
    ]

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHERS')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - £{self.amount}"