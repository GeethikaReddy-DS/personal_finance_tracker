from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction

@login_required
def dashboard(request):
    income = Transaction.objects.filter(
        user=request.user,
        category__type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    expense = Transaction.objects.filter(
        user=request.user,
        category__type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'dashboard.html', {
        'income': income,
        'expense': expense,
        'savings': income - expense
    })

