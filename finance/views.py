# views.py — MoneyMate dashboard logic

from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from .models import Income, Expense
from .forms import ExpenseForm, IncomeForm


def dashboard(request):

    # --- Handle form submissions ---
    if request.method == 'POST':

        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('dashboard')

        elif 'add_income' in request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('dashboard')

    # --- Fetch all records ---
    incomes  = Income.objects.all()
    expenses = Expense.objects.all()

    # --- Calculate totals ---
    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    leftover       = total_income - total_expenses

    # --- Savings intelligence benchmarks ---
    # These are monthly averages used to flag overspending.
    # One benchmark per category — no duplicates possible.
    benchmarks = {
        'UTILITIES':     Decimal('150.00'),
        'SUBSCRIPTIONS': Decimal('40.00'),
        'GROCERIES':     Decimal('400.00'),
        'INSURANCE':     Decimal('120.00'),
        'MOBILE':        Decimal('25.00'),
        'FUEL':          Decimal('100.00'),
        'LOANS':         Decimal('300.00'),
        'MORTGAGE':      Decimal('800.00'),
        'DEBTS':         Decimal('50.00'),
    }

    recommendations = []

    # Loop over each category once — sum ALL bills in that category together,
    # then compare the combined total to the benchmark.
    # This prevents the same category appearing multiple times.
    for cat_code, cat_name in Expense.CATEGORY_CHOICES:
        if cat_code not in benchmarks:
            continue

        # Sum every expense in this category
        cat_expenses = [e for e in expenses if e.category == cat_code]
        cat_total    = sum(e.amount for e in cat_expenses)

        if cat_total == 0:
            continue  # user has no bills in this category — skip

        if cat_total > benchmarks[cat_code]:
            savings = cat_total - benchmarks[cat_code]

            # Collect company names for all bills in this category
            # e.g. ["Admiral", "Aviva"] — shown in the tip so user knows which bills triggered it
            companies = [e.company for e in cat_expenses if e.company]

            recommendations.append({
                'category':        cat_name,
                'spent':           cat_total,
                'average':         benchmarks[cat_code],
                'potential_saving': savings,
                'companies':       companies,  # passed to template for display
            })

    # --- Build context for the template ---
    context = {
        'total_income':   total_income,
        'total_expenses': total_expenses,
        'leftover':       leftover,
        'expenses':       expenses,
        'incomes':        incomes,
        'expense_form':   ExpenseForm(),
        'income_form':    IncomeForm(),
        'recommendations': recommendations,
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