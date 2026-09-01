# views.py — MoneyMate views

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as django_settings
from decimal import Decimal
from datetime import date
import calendar
from .models import Income, Expense, SavingsGoal, UserProfile
from .forms import ExpenseForm, IncomeForm, SavingsGoalForm, RegisterForm, ProfileForm, EmailChangeForm, SupportContactForm


# --- Helper: get the month/year being viewed from the request ---
# Falls back to the current month if no query params are provided
def get_active_month(request):
    today = date.today()
    try:
        month = int(request.GET.get('month', today.month))
        year  = int(request.GET.get('year', today.year))
    except (ValueError, TypeError):
        month, year = today.month, today.year
    month = max(1, min(12, month))
    return month, year


# --- Helper: build prev/next month navigation values ---
def month_nav(month, year):
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return {
        'month':      month,
        'year':       year,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month,
        'prev_year':  prev_year,
        'next_month': next_month,
        'next_year':  next_year,
    }


# --- Helper: rollover recurring records from the previous month ---
# Copies fixed income and fixed recurring bills if this month has no records yet
def rollover_if_needed(user, month, year):
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    has_income   = Income.objects.filter(user=user, month=month, year=year).exists()
    has_expenses = Expense.objects.filter(user=user, month=month, year=year).exists()

    if not has_income:
        # Copy recurring income from the previous month
        prev_incomes = Income.objects.filter(user=user, month=prev_month, year=prev_year, is_recurring=True)
        for inc in prev_incomes:
            Income.objects.create(
                user=user, source=inc.source, amount=inc.amount,
                month=month, year=year, is_recurring=True,
            )

    if not has_expenses:
        # Copy fixed recurring bills — one-off and variable stay behind
        prev_expenses = Expense.objects.filter(
            user=user, month=prev_month, year=prev_year
        ).exclude(frequency='ONE_OFF').filter(bill_type='FIXED')

        for exp in prev_expenses:
            Expense.objects.create(
                user=exp.user, name=exp.name, company=exp.company,
                amount=exp.amount, category=exp.category, sub_type=exp.sub_type,
                frequency=exp.frequency, bill_type=exp.bill_type,
                month=month, year=year,
                customer_number=exp.customer_number,
                tariff_details=exp.tariff_details,
                start_date=exp.start_date, end_date=exp.end_date,
            )


# --- UK market benchmarks used by the intelligence engine ---
BENCHMARKS = {
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


# --- Landing page ---
def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'finance/landing.html')


# --- Dashboard ---
@login_required
def dashboard(request):
    month, year = get_active_month(request)
    rollover_if_needed(request.user, month, year)

    if request.method == 'POST':
        if 'add_expense' in request.POST:
            form = ExpenseForm(request.POST)
            if form.is_valid():
                expense       = form.save(commit=False)
                expense.user  = request.user
                expense.month = month
                expense.year  = year
                expense.save()
                return redirect(f'/dashboard/?month={month}&year={year}')

        elif 'add_income' in request.POST:
            form = IncomeForm(request.POST)
            if form.is_valid():
                income       = form.save(commit=False)
                income.user  = request.user
                income.month = month
                income.year  = year
                income.save()
                return redirect(f'/dashboard/?month={month}&year={year}')

    incomes  = Income.objects.filter(user=request.user, month=month, year=year)
    expenses = Expense.objects.filter(user=request.user, month=month, year=year)

    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.monthly_amount() for e in expenses)
    leftover       = total_income - total_expenses

    # Build intelligence recommendations for this month
    recommendations = []
    for cat_code, cat_name in Expense.CATEGORY_CHOICES:
        if cat_code not in BENCHMARKS:
            continue
        cat_expenses = [e for e in expenses if e.category == cat_code]
        cat_total    = sum(e.monthly_amount() for e in cat_expenses)
        if cat_total == 0:
            continue
        if cat_total > BENCHMARKS[cat_code]:
            savings   = cat_total - BENCHMARKS[cat_code]
            companies = [e.company for e in cat_expenses if e.company]
            recommendations.append({
                'category':         cat_name,
                'spent':            round(cat_total, 2),
                'average':          BENCHMARKS[cat_code],
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
        **month_nav(month, year),
    }

    return render(request, 'finance/dashboard.html', context)


# --- Income page ---
@login_required
def income_page(request):
    month, year = get_active_month(request)
    rollover_if_needed(request.user, month, year)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income       = form.save(commit=False)
            income.user  = request.user
            income.month = month
            income.year  = year
            income.save()
            return redirect(f'/income/?month={month}&year={year}')

    incomes      = Income.objects.filter(user=request.user, month=month, year=year).order_by('-date_added')
    total_income = sum(i.amount for i in incomes)
    form         = IncomeForm()

    context = {
        'incomes':      incomes,
        'total_income': total_income,
        'form':         form,
        **month_nav(month, year),
    }

    return render(request, 'finance/income.html', context)


# --- Bills page ---
@login_required
def bills_page(request):
    month, year = get_active_month(request)
    rollover_if_needed(request.user, month, year)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense       = form.save(commit=False)
            expense.user  = request.user
            expense.month = month
            expense.year  = year
            expense.save()
            return redirect(f'/bills/?month={month}&year={year}')

    category_filter = request.GET.get('category', '')
    expenses = Expense.objects.filter(user=request.user, month=month, year=year).order_by('-date_added')
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    total_expenses = sum(
        e.monthly_amount() for e in Expense.objects.filter(user=request.user, month=month, year=year)
    )
    form = ExpenseForm()

    context = {
        'expenses':        expenses,
        'total_expenses':  round(total_expenses, 2),
        'form':            form,
        'category_filter': category_filter,
        'categories':      Expense.CATEGORY_CHOICES,
        **month_nav(month, year),
    }

    return render(request, 'finance/bills.html', context)


# --- Compare & Save: Car Insurance ---
@login_required
def compare_insurance(request):
    bills       = Expense.objects.filter(user=request.user, category='INSURANCE', sub_type='INS_CAR')
    total_spent = sum(e.monthly_amount() for e in bills)
    context = {
        'bills':       bills,
        'total_spent': round(total_spent, 2),
        'benchmark':   Decimal('80.00'),
    }
    return render(request, 'finance/compare_insurance.html', context)


# --- Compare & Save: Energy ---
@login_required
def compare_energy(request):
    bills       = Expense.objects.filter(
        user=request.user, category='UTILITIES', sub_type__in=['UTIL_GAS', 'UTIL_ELECTRIC']
    )
    total_spent = sum(e.monthly_amount() for e in bills)
    context = {
        'bills':       bills,
        'total_spent': round(total_spent, 2),
        'benchmark':   Decimal('150.00'),
    }
    return render(request, 'finance/compare_energy.html', context)


# --- Compare & Save: Broadband ---
@login_required
def compare_broadband(request):
    bills       = Expense.objects.filter(
        user=request.user, category='UTILITIES', sub_type='UTIL_BROADBAND'
    )
    total_spent = sum(e.monthly_amount() for e in bills)
    context = {
        'bills':       bills,
        'total_spent': round(total_spent, 2),
        'benchmark':   Decimal('40.00'),
    }
    return render(request, 'finance/compare_broadband.html', context)


# --- Compare & Save: Home Insurance ---
@login_required
def compare_home(request):
    bills       = Expense.objects.filter(user=request.user, category='INSURANCE', sub_type='INS_HOME')
    total_spent = sum(e.monthly_amount() for e in bills)
    context = {
        'bills':       bills,
        'total_spent': round(total_spent, 2),
        'benchmark':   Decimal('40.00'),
    }
    return render(request, 'finance/compare_home.html', context)


# --- Savings Goals ---
@login_required
def savings_goals(request):
    month, year = get_active_month(request)

    incomes  = Income.objects.filter(user=request.user, month=month, year=year)
    expenses = Expense.objects.filter(user=request.user, month=month, year=year)

    total_income   = sum(i.amount for i in incomes)
    total_expenses = sum(e.monthly_amount() for e in expenses)
    leftover       = total_income - total_expenses

    suggested_contribution = round(leftover * Decimal('0.20'), 2) if leftover > 0 else Decimal('0.00')

    if request.method == 'POST':
        if 'add_goal' in request.POST:
            form = SavingsGoalForm(request.POST)
            if form.is_valid():
                goal      = form.save(commit=False)
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
    # get_object_or_404 with user= prevents users deleting each other's bills
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# --- Delete income ---
@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    


# --- Register ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user       = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            login(request, user)
            return redirect('dashboard')
        # If form is invalid, re-render with errors
    else:
        form = RegisterForm()

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
    return redirect('landing')


# --- Profile ---
@login_required
def profile_view(request):
    user    = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user, initial={
            'occupation': profile.occupation,
            'location':   profile.location,
            'phone':      profile.phone,
            'bio':        profile.bio,
        })
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user, initial={
            'occupation': profile.occupation,
            'location':   profile.location,
            'phone':      profile.phone,
            'bio':        profile.bio,
        })

    income_count = Income.objects.filter(user=user).values('source').distinct().count()
    bills_count  = Expense.objects.filter(user=user).values('name').distinct().count()
    goals        = SavingsGoal.objects.filter(user=user)
    total_saved  = sum(g.current_amount for g in goals)

    return render(request, 'finance/profile.html', {
        'form':         form,
        'profile':      profile,
        'income_count': income_count,
        'bills_count':  bills_count,
        'goals_count':  goals.count(),
        'total_saved':  total_saved,
        **month_nav(*get_active_month(request)),
    })


# --- Settings ---
@login_required
def settings_view(request):
    user          = request.user
    pw_form       = PasswordChangeForm(user)
    email_form    = EmailChangeForm(user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_password':
            pw_form = PasswordChangeForm(user, request.POST)
            if pw_form.is_valid():
                pw_form.save()
                update_session_auth_hash(request, pw_form.user)
                messages.success(request, 'Password changed successfully.')
                return redirect('settings')
            else:
                messages.error(request, 'Please fix the errors below.')

        elif action == 'change_email':
            email_form = EmailChangeForm(user, request.POST)
            if email_form.is_valid():
                user.email = email_form.cleaned_data['email']
                user.save()
                messages.success(request, 'Email address updated.')
                return redirect('settings')
            else:
                messages.error(request, 'Please fix the errors below.')

        elif action == 'delete_account':
            confirm = request.POST.get('confirm_username', '').strip()
            if confirm == user.username:
                user.delete()
                messages.success(request, 'Your account has been deleted.')
                return redirect('landing')
            else:
                messages.error(request, 'Username did not match — account not deleted.')

    return render(request, 'finance/settings.html', {
        'pw_form':    pw_form,
        'email_form': email_form,
        **month_nav(*get_active_month(request)),
    })


# --- Support ---
@login_required
def support_view(request):
    contact_form = SupportContactForm()

    if request.method == 'POST':
        contact_form = SupportContactForm(request.POST)
        if contact_form.is_valid():
            send_mail(
                subject=f"[MoneyMate Support] {contact_form.cleaned_data['subject']}",
                message=(
                    f"From: {request.user.username} ({request.user.email})\n\n"
                    f"{contact_form.cleaned_data['message']}"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[django_settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
            messages.success(request, 'Message sent — we\'ll get back to you soon.')
            return redirect('support')

    return render(request, 'finance/support.html', {
        'contact_form': contact_form,
        **month_nav(*get_active_month(request)),
    })