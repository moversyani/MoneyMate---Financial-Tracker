# views.py — MoneyMate views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Income, Expense, SavingsGoal
from .forms import ExpenseForm, IncomeForm, SavingsGoalForm


# --- Landing page ---
# Shown at / — redirects logged-in users straight to the dashboard
def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'finance/landing.html')


# --- Dashboard ---
@login_required
def dashboard(request):

    if request.method == 'POST':

        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('dashboard')

        elif 'add_income' in request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                income = form.save(commit=False)
                income.user = request.user
                income.save()
                return redirect('dashboard')

    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.monthly_amount() for e in expenses)
    leftover       = total_income - total_expenses

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

    for cat_code, cat_name in Expense.CATEGORY_CHOICES:
        if cat_code not in benchmarks:
            continue
        cat_expenses = [e for e in expenses if e.category == cat_code]
        cat_total    = sum(e.monthly_amount() for e in cat_expenses)
        if cat_total == 0:
            continue
        if cat_total > benchmarks[cat_code]:
            savings   = cat_total - benchmarks[cat_code]
            companies = [e.company for e in cat_expenses if e.company]
            recommendations.append({
                'category':         cat_name,
                'spent':            round(cat_total, 2),
                'average':          benchmarks[cat_code],
                'potential_saving': round(savings, 2),
                'companies':        companies,
            })

    goals = SavingsGoal.objects.filter(user=request.user)

    context = {
        'total_income':    total_income,
        'total_expenses':  round(total_expenses, 2),
        'leftover':        round(leftover, 2),
        'expenses':        expenses,
        'incomes':         incomes,
        'expense_form':    ExpenseForm(),
        'income_form':     IncomeForm(),
        'recommendations': recommendations,
        'goals':           goals,
    }

    return render(request, 'finance/dashboard.html', context)


# --- Savings Goals full page ---
@login_required
def savings_goals(request):

    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.monthly_amount() for e in expenses)
    leftover       = total_income - total_expenses

    # Suggest 20% of disposable income as the monthly contribution
    suggested_contribution = round(leftover * Decimal('0.20'), 2) if leftover > 0 else Decimal('0.00')

    if request.method == 'POST':

        if 'add_goal' in request.POST:
            form = SavingsGoalForm(request.POST)
            if form.is_valid():
                goal = form.save(commit=False)
                goal.user = request.user
                goal.save()
                return redirect('savings_goals')

        elif 'add_contribution' in request.POST:
            goal_id = request.POST.get('goal_id')
            amount  = request.POST.get('contribution_amount')
            goal    = get_object_or_404(SavingsGoal, pk=goal_id, user=request.user)
            try:
                goal.current_amount += Decimal(amount)
                goal.save()
            except Exception:
                pass
            return redirect('savings_goals')

    goals = SavingsGoal.objects.filter(user=request.user)
    form  = SavingsGoalForm(initial={'monthly_contribution': suggested_contribution})

    context = {
        'goals':                  goals,
        'form':                   form,
        'leftover':               round(leftover, 2),
        'suggested_contribution': suggested_contribution,
    }

    return render(request, 'finance/savings.html', context)


# --- Delete savings goal ---
@login_required
def delete_goal(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    goal.delete()
    return redirect('savings_goals')


# --- Delete expense ---
@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('dashboard')


# --- Delete income ---
@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect('dashboard')


# --- Register ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to MoneyMate, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'finance/register.html', {'form': form})


# --- Login ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'finance/login.html', {'form': form})


# --- Logout ---
@login_required
def logout_view(request):
    logout(request)
    return redirect('landing')  # send back to landing page after logout