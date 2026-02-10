from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Q, F
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from .models import Transaction, Category, UserProfile, Receipt
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    UserPreferenceForm, CategoryForm, TransactionForm,
    TransactionFilterForm, ReceiptForm
)
from budgets.models import Budget, Notification


# ==================== Authentication Views ====================

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # UserProfile is created automatically by the signal in models
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile(request):
    """User profile view"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        pref_form = UserPreferenceForm(request.POST, instance=profile)

        if user_form.is_valid() and pref_form.is_valid():
            user_form.save()
            pref_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        pref_form = UserPreferenceForm(instance=profile)

    context = {
        'user_form': user_form,
        'pref_form': pref_form,
        'profile': profile,
    }
    return render(request, 'auth/profile.html', context)


# ==================== Dashboard Views ====================

@login_required
def dashboard(request):
    """Dashboard with overview of financial status"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Get date range for current month
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Current month statistics
    month_transactions = Transaction.objects.filter(user=request.user, date__range=[month_start, month_end])
    month_income = month_transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    month_expense = month_transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Total statistics (all time)
    all_income = Transaction.objects.filter(user=request.user, category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    all_expense = Transaction.objects.filter(user=request.user, category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Budget warnings
    budget_warnings = []
    budgets = Budget.objects.filter(user=request.user)
    for budget in budgets:
        if budget.is_over_budget:
            budget_warnings.append({
                'budget': budget,
                'overspent': budget.spent - budget.limit
            })

    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user)[:10]

    # Expense breakdown for current month
    expense_breakdown = month_transactions.filter(
        category__type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')

    # Income breakdown for current month
    income_breakdown = month_transactions.filter(
        category__type='income'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'profile': profile,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_savings': month_income - month_expense,
        'all_income': all_income,
        'all_expense': all_expense,
        'all_savings': all_income - all_expense,
        'recent_transactions': recent_transactions,
        'budget_warnings': budget_warnings,
        'expense_breakdown': list(expense_breakdown),
        'income_breakdown': list(income_breakdown),
        'month_start': month_start,
        'month_end': month_end,
    }

    return render(request, 'dashboard.html', context)


# ==================== Category Management ====================

@login_required
def category_list(request):
    """List all categories for the user"""
    categories = Category.objects.filter(user=request.user).order_by('type', 'name')
    income_categories = categories.filter(type='income')
    expense_categories = categories.filter(type='expense')

    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    }
    return render(request, 'categories/category_list.html', context)


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'categories/category_form.html', {'form': form})


@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        category_name = category.name
        # Move orphaned transactions to NULL category
        Transaction.objects.filter(category=category).update(category=None)
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('category_list')

    return render(request, 'categories/category_confirm_delete.html', {'category': category})


# ==================== Transaction Management ====================

@login_required
def transaction_list(request):
    """List transactions with filtering"""
    transactions = Transaction.objects.filter(user=request.user)
    form = TransactionFilterForm(request.GET, user=request.user)

    if form.is_valid():
        if form.cleaned_data.get('start_date'):
            transactions = transactions.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            transactions = transactions.filter(date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data.get('category'):
            transactions = transactions.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('transaction_type'):
            transactions = transactions.filter(category__type=form.cleaned_data['transaction_type'])

    context = {
        'transactions': transactions,
        'form': form,
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
def transaction_create(request):
    """Create a new transaction"""
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user

            # Handle receipt upload
            if form.cleaned_data.get('receipt_file'):
                receipt = Receipt.objects.create(
                    user=request.user,
                    file=form.cleaned_data['receipt_file']
                )
                transaction.receipt = receipt

            transaction.clean()
            transaction.save()

            # Update budget spent amount
            if transaction.category and transaction.category.type == 'expense':
                try:
                    budget = Budget.objects.get(user=request.user, category=transaction.category)
                    budget.spent = Decimal(str(budget.spent)) + transaction.amount
                    budget.save()

                    # Create notification if over budget
                    if budget.is_over_budget:
                        Notification.objects.create(
                            user=request.user,
                            notification_type='budget_exceeded',
                            title=f'Budget Exceeded: {budget.category.name}',
                            message=f'You have exceeded your budget for {budget.category.name}. Spent: {budget.spent}, Limit: {budget.limit}',
                            budget=budget
                        )
                except Budget.DoesNotExist:
                    pass

            messages.success(request, 'Transaction created successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)

    has_categories = Category.objects.filter(user=request.user).exists()

    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'action': 'Create',
        'has_categories': has_categories,
    })


@login_required
def transaction_edit(request, pk):
    """Edit a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    old_amount = transaction.amount

    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)

            # Handle receipt upload
            if form.cleaned_data.get('receipt_file'):
                if transaction.receipt:
                    transaction.receipt.file.delete()
                receipt = Receipt.objects.create(
                    user=request.user,
                    file=form.cleaned_data['receipt_file']
                )
                transaction.receipt = receipt

            transaction.clean()
            transaction.save()

            # Update budget if amount changed
            if old_amount != transaction.amount and transaction.category and transaction.category.type == 'expense':
                try:
                    budget = Budget.objects.get(user=request.user, category=transaction.category)
                    difference = transaction.amount - old_amount
                    budget.spent = Decimal(str(budget.spent)) + difference
                    budget.save()
                except Budget.DoesNotExist:
                    pass

            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    has_categories = Category.objects.filter(user=request.user).exists()

    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'action': 'Edit',
        'transaction': transaction,
        'has_categories': has_categories,
    })


@login_required
def transaction_delete(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        # Update budget
        if transaction.category and transaction.category.type == 'expense':
            try:
                budget = Budget.objects.get(user=request.user, category=transaction.category)
                budget.spent = max(Decimal('0'), Decimal(str(budget.spent)) - transaction.amount)
                budget.save()
            except Budget.DoesNotExist:
                pass

        # Delete receipt if exists
        if transaction.receipt:
            transaction.receipt.file.delete()
            transaction.receipt.delete()

        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')

    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': transaction})


# ==================== Reporting Views ====================

@login_required
def report_monthly(request):
    """Monthly income vs expense report"""
    month = request.GET.get('month')
    year = request.GET.get('year')

    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year
    else:
        month = int(month)
        year = int(year)

    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    transactions = Transaction.objects.filter(user=request.user, date__range=[month_start, month_end])

    month_income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    month_expense = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    income_by_category = transactions.filter(category__type='income').values('category__name').annotate(total=Sum('amount')).order_by('-total')
    expense_by_category = transactions.filter(category__type='expense').values('category__name').annotate(total=Sum('amount')).order_by('-total')

    context = {
        'month': month,
        'year': year,
        'month_start': month_start,
        'month_end': month_end,
        'month_income': month_income,
        'month_expense': month_expense,
        'month_savings': month_income - month_expense,
        'income_by_category': list(income_by_category),
        'expense_by_category': list(expense_by_category),
    }

    return render(request, 'reports/report_monthly.html', context)


@login_required
def report_yearly(request):
    """Yearly income vs expense report"""
    year = request.GET.get('year')

    if not year:
        year = date.today().year
    else:
        year = int(year)

    yearly_data = []
    for month in range(1, 13):
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)

        transactions = Transaction.objects.filter(user=request.user, date__range=[month_start, month_end])
        income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        yearly_data.append({
            'month': month,
            'month_name': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1],
            'income': income,
            'expense': expense,
            'savings': income - expense,
        })

    yearly_income = sum(d['income'] for d in yearly_data)
    yearly_expense = sum(d['expense'] for d in yearly_data)

    context = {
        'year': year,
        'yearly_data': yearly_data,
        'yearly_income': yearly_income,
        'yearly_expense': yearly_expense,
        'yearly_savings': yearly_income - yearly_expense,
    }

    return render(request, 'reports/report_yearly.html', context)


@login_required
def report_category(request):
    """Category-wise spending report"""
    category_type = request.GET.get('type', 'expense')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    transactions = Transaction.objects.filter(user=request.user, category__type=category_type)

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    from django.db.models import Count
    category_data = transactions.values('category__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    total = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    for item in category_data:
        item['percentage'] = (item['total'] / total * 100) if total > 0 else 0

    context = {
        'category_type': category_type,
        'category_data': list(category_data),
        'total': total,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }

    return render(request, 'reports/report_category.html', context)


# ==================== AJAX API Views ====================

@login_required
@require_http_methods(["GET"])
def api_dashboard_data(request):
    """API endpoint for dashboard data (for charts)"""
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

    transactions = Transaction.objects.filter(user=request.user, date__range=[month_start, month_end])

    expense_breakdown = transactions.filter(category__type='expense').values('category__name').annotate(total=Sum('amount')).order_by('-total')
    income_breakdown = transactions.filter(category__type='income').values('category__name').annotate(total=Sum('amount')).order_by('-total')

    month_income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    month_expense = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    return JsonResponse({
        'month_income': float(month_income),
        'month_expense': float(month_expense),
        'month_savings': float(month_income - month_expense),
        'expense_breakdown': list(expense_breakdown),
        'income_breakdown': list(income_breakdown),
    })


@login_required
@require_http_methods(["GET"])
def api_monthly_trend(request):
    """API endpoint for monthly trend data"""
    months = int(request.GET.get('months', 6))
    today = date.today()

    data = []
    for i in range(months, 0, -1):
        month_date = today - timedelta(days=i * 30)
        month_start = date(month_date.year, month_date.month, 1)
        if month_date.month == 12:
            month_end = date(month_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_date.year, month_date.month + 1, 1) - timedelta(days=1)

        transactions = Transaction.objects.filter(user=request.user, date__range=[month_start, month_end])
        income = transactions.filter(category__type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = transactions.filter(category__type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        data.append({
            'month': month_date.strftime('%B %Y'),
            'income': float(income),
            'expense': float(expense),
            'savings': float(income - expense),
        })

    return JsonResponse({'data': data})


