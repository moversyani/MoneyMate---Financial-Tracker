# views.py — MoneyMate views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Income, Expense
from .forms import ExpenseForm, IncomeForm


# --- Dashboard view ---
# @login_required redirects to /login/ if the user is not authenticated
@login_required
def dashboard(request):

    # Handle form submissions
    if request.method == 'POST':

        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                # Save the bill but assign the current user before committing
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('dashboard')

        elif 'add_income' in request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                # Save the income but assign the current user before committing
                income = form.save(commit=False)
                income.user = request.user
                income.save()
                return redirect('dashboard')

    # Filter all queries by the logged-in user so users only see their own data
    incomes  = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    # Calculate totals from the user's own records only
    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.amount for e in expenses)
    leftover       = total_income - total_expenses

    # Savings intelligence benchmarks (monthly averages)
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

    # Sum all bills per category — one tip per category, no duplicates
    for cat_code, cat_name in Expense.CATEGORY_CHOICES:
        if cat_code not in benchmarks:
            continue

        cat_expenses = [e for e in expenses if e.category == cat_code]
        cat_total    = sum(e.amount for e in cat_expenses)

        if cat_total == 0:
            continue

        if cat_total > benchmarks[cat_code]:
            savings   = cat_total - benchmarks[cat_code]
            companies = [e.company for e in cat_expenses if e.company]

            recommendations.append({
                'category':         cat_name,
                'spent':            cat_total,
                'average':          benchmarks[cat_code],
                'potential_saving': savings,
                'companies':        companies,
            })

    context = {
        'total_income':    total_income,
        'total_expenses':  total_expenses,
        'leftover':        leftover,
        'expenses':        expenses,
        'incomes':         incomes,
        'expense_form':    ExpenseForm(),
        'income_form':     IncomeForm(),
        'recommendations': recommendations,
    }

    return render(request, 'finance/dashboard.html', context)


# --- Delete expense ---
@login_required
def delete_expense(request, pk):
    # get_object_or_404 also checks the record belongs to the current user
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect('dashboard')


# --- Delete income ---
@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect('dashboard')


# --- Register view ---
def register_view(request):
    # Redirect already logged-in users straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after registering
            login(request, user)
            messages.success(request, f'Welcome to MoneyMate, {user.username}!')
            return redirect('dashboard')
        else:
            # Show form errors back to the user
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'finance/register.html', {'form': form})


# --- Login view ---
def login_view(request):
    # Redirect already logged-in users straight to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # If user was redirected to login from another page, send them back there
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'finance/login.html', {'form': form})


# --- Logout view ---
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')