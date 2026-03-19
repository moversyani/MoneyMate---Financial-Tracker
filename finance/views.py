from django.shortcuts import render, redirect, get_object_or_404 # Added get_object_or_404
from .models import Income, Expense
from .forms import ExpenseForm, IncomeForm

def dashboard(request):
    # Logic for handling form submissions
    if request.method == 'POST':
        if 'add_expense' in request.POST:
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense_form.save()
                return redirect('dashboard')
        
        elif 'add_income' in request.POST:
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income_form.save()
                return redirect('dashboard')
    
    # If not a POST, provide blank forms
    expense_form = ExpenseForm()
    income_form = IncomeForm()

    # Data fetching
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
        'incomes': incomes, # For displaying incomes
        'expense_form': expense_form,
        'income_form': income_form,
    }
    return render(request, 'finance/dashboard.html', context)


def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    return redirect('dashboard')


def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk)
    income.delete()
    return redirect('dashboard')