from django.shortcuts import render
from .models import Income, Expense # Import the tables we built

def dashboard(request):
    # Retrieve all financial data from the database
    # .all() fetches every row in that specific table
    incomes = Income.objects.all()
    expenses = Expense.objects.all()

    # Calculate the math for the "Overview" section
    # sum() adds up the 'amount' field for every item found
    total_income = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    leftover = total_income - total_expenses

    # The 'context' is like a delivery box sending data to the HTML
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'leftover': leftover,
        'expenses': expenses, # We send the full list to show the bills
    }

    # Tell Django to find the file in the folder you just created
    return render(request, 'finance/dashboard.html', context)