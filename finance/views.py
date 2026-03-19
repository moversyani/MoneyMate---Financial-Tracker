from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from .models import Income, Expense
from .forms import ExpenseForm, IncomeForm

def dashboard(request):
    # 1. Handle Form Submissions
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

    # 2. Fetch Data
    incomes = Income.objects.all()
    expenses = Expense.objects.all()
    
    # 3. Calculate Totals
    total_income = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    leftover = total_income - total_expenses

    # 4. SAVINGS ENGINE LOGIC
    benchmarks = {
        'UTILITIES': Decimal('150.00'),
        'SUBSCRIPTIONS': Decimal('40.00'),
        'GROCERIES': Decimal('400.00'),
        'INSURANCE': Decimal('120.00'),
    }

    recommendations = []
    
    for cat_code, cat_name in Expense.CATEGORY_CHOICES:
        cat_total = sum(e.amount for e in expenses if e.category == cat_code)
        
        if cat_code in benchmarks and cat_total > benchmarks[cat_code]:
            savings = cat_total - benchmarks[cat_code]
            recommendations.append({
                'category': cat_name,
                'spent': cat_total,
                'average': benchmarks[cat_code],
                'potential_saving': savings
            })

    # 5. Build Context
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'leftover': leftover,
        'expenses': expenses,
        'incomes': incomes,
        'expense_form': ExpenseForm(),
        'income_form': IncomeForm(),
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