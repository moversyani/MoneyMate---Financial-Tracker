from django.shortcuts import render, redirect, get_object_or_404 # Added get_object_or_404
from .models import Income, Expense
from .forms import ExpenseForm

def dashboard(request):
    # Logic for handling a new bill submission
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('dashboard') 
    else:
        form = ExpenseForm() 

    # Data fetching logic
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
        'form': form,
    }
    return render(request, 'finance/dashboard.html', context)


def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('dashboard')