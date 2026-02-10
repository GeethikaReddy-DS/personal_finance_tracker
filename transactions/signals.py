from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal
from datetime import date
from .models import UserProfile, Transaction, Category
import sys
from budgets.models import Budget


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

        # Create some default categories for new users (skip during test runs)
        if 'test' in sys.argv:
            return

        default_income = ['Salary', 'Investment', 'Gift']
        default_expense = ['Groceries', 'Rent', 'Utilities', 'Transport', 'Entertainment']

        # Only create defaults if the user has no categories yet
        if not Category.objects.filter(user=instance).exists():
            for name in default_income:
                Category.objects.create(user=instance, name=name, type='income')
            for name in default_expense:
                Category.objects.create(user=instance, name=name, type='expense')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Transaction)
def update_budget_on_transaction_save(sender, instance, created, **kwargs):
    """Update budget when a transaction is saved"""
    if instance.category and instance.category.type == 'expense':
        try:
            budget = Budget.objects.get(user=instance.user, category=instance.category)
            # Recalculate all spent for this budget
            transactions = Transaction.objects.filter(
                user=instance.user,
                category=instance.category
            )
            
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
            
            budget.spent = transactions.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')
            budget.save()
        except Budget.DoesNotExist:
            pass


@receiver(post_delete, sender=Transaction)
def update_budget_on_transaction_delete(sender, instance, **kwargs):
    """Update budget when a transaction is deleted"""
    if instance.category and instance.category.type == 'expense':
        try:
            budget = Budget.objects.get(user=instance.user, category=instance.category)
            budget.spent = max(Decimal('0'), budget.spent - instance.amount)
            budget.save()
        except Budget.DoesNotExist:
            pass
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
