from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date

from .models import Budget, Notification
from .forms import BudgetForm


@login_required
def budget_list(request):
    """List all budgets for the user"""
    budgets = Budget.objects.filter(user=request.user).select_related('category')
    
    # Calculate current spending for each budget
    for budget in budgets:
        category_transactions = budget.category.transaction_set.filter(user=request.user)
        
        # Filter by period
        if budget.period == 'monthly':
            today = date.today()
            from datetime import datetime
            category_transactions = category_transactions.filter(
                date__year=today.year,
                date__month=today.month
            )
        elif budget.period == 'yearly':
            today = date.today()
            category_transactions = category_transactions.filter(date__year=today.year)
        
        spent = category_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
        budget.spent = spent
        budget.save()

    context = {
        'budgets': budgets,
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_create(request):
    """Create a new budget"""
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.clean()
            budget.save()
            messages.success(request, f'Budget for "{budget.category.name}" created successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(user=request.user)

    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Create'})


@login_required
def budget_edit(request, pk):
    """Edit a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.clean()
            budget.save()
            messages.success(request, f'Budget for "{budget.category.name}" updated successfully!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=budget, user=request.user)

    return render(request, 'budgets/budget_form.html', {'form': form, 'action': 'Edit', 'budget': budget})


@login_required
def budget_delete(request, pk):
    """Delete a budget"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST':
        budget_name = budget.category.name
        budget.delete()
        messages.success(request, f'Budget for "{budget_name}" deleted successfully!')
        return redirect('budget_list')

    return render(request, 'budgets/budget_confirm_delete.html', {'budget': budget})


@login_required
def budget_detail(request, pk):
    """View budget details"""
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    
    # Get transactions for this budget's category
    transactions = budget.category.transaction_set.filter(user=request.user)
    
    # Filter by period
    if budget.period == 'monthly':
        today = date.today()
        transactions = transactions.filter(
            date__year=today.year,
            date__month=today.month
        )
    elif budget.period == 'yearly':
        today = date.today()
        transactions = transactions.filter(date__year=today.year)

    context = {
        'budget': budget,
        'transactions': transactions,
    }
    return render(request, 'budgets/budget_detail.html', context)


@login_required
def notification_list(request):
    """List notifications for the user"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'mark_all_read':
            notifications.update(is_read=True)
            messages.success(request, 'All notifications marked as read.')
            return redirect('notification_list')

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_mark_read(request, pk):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.GET.get('next'):
        return redirect(request.GET.get('next'))
    return redirect('notification_list')
