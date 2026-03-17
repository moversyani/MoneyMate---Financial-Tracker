from django.shortcuts import render, redirect # Added redirect
from .models import Income, Expense
from .forms import ExpenseForm # Import the form we just made

def dashboard(request):
    # Logic for handling a new bill submission
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save() # Saves the new bill directly to the database
            return redirect('dashboard') # Refresh the page to show new data
    else:
        form = ExpenseForm() # Provide a blank form if just visiting the page

    # Existing data fetching logic
    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    total_income = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    leftover = total_income - total_expenses

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'leftover': leftover,
        'expenses': expenses,
        'form': form, # Pass the form to the HTML template
    }
    return render(request, 'finance/dashboard.html', context)