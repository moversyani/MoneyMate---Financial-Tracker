# views.py — MoneyMate views
# Controls what each URL renders and what logic runs when forms are submitted

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal  # used for precise money arithmetic — avoids float rounding errors
from .models import Income, Expense
from .forms import ExpenseForm, IncomeForm


# --- Dashboard ---
# @login_required redirects unauthenticated users to /login/ automatically
@login_required
def dashboard(request):

    if request.method == 'POST':

        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                expense = form.save(commit=False)  # create object without saving yet
                expense.user = request.user        # attach the logged-in user before saving
                expense.save()
                return redirect('dashboard')

        elif 'add_income' in request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                income = form.save(commit=False)
                income.user = request.user
                income.save()
                return redirect('dashboard')

    # filter(user=request.user) ensures users only see their own records
    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income   = sum(i.amount for i in incomes)
    # monthly_amount() normalises annual bills to monthly before totalling
    total_expenses = sum(e.monthly_amount() for e in expenses)
    leftover       = total_income - total_expenses

    # UK market average benchmarks — used to flag overspending per category
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
            # collect company names from all bills in this category for the tip card
            companies = [e.company for e in cat_expenses if e.company]

            recommendations.append({
                'category':         cat_name,
                'spent':            round(cat_total, 2),
                'average':          benchmarks[cat_code],
                'potential_saving': round(savings, 2),
                'companies':        companies,
            })

    # context dict passes all data to dashboard.html — every {{ variable }} maps to a key here
    context = {
        'total_income':    total_income,
        'total_expenses':  round(total_expenses, 2),
        'leftover':        round(leftover, 2),
        'expenses':        expenses,
        'incomes':         incomes,
        'expense_form':    ExpenseForm(),
        'income_form':     IncomeForm(),
        'recommendations': recommendations,
    }

    return render(request, 'finance/dashboard.html', context)


# --- Delete expense ---
# get_object_or_404 with user=request.user prevents users deleting each other's bills
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
# Uses Django's built-in UserCreationForm — handles validation automatically
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # skip signup if already logged in

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log the user in immediately after registering
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
            # if user was redirected here from another page, send them back after login
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
    logout(request)          # clears the user's session
    return redirect('login')