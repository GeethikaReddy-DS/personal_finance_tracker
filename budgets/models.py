from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from transactions.models import Category
from datetime import date


class Budget(models.Model):
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category']
        unique_together = ('user', 'category', 'period')

    def clean(self):
        if self.limit <= 0:
            raise ValidationError("Budget limit must be greater than 0")
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date")
        if self.category.type != 'expense':
            raise ValidationError("Budget can only be set for expense categories")

    @property
    def remaining(self):
        """Calculate remaining budget"""
        return self.limit - self.spent

    @property
    def percentage_used(self):
        """Calculate percentage of budget used"""
        if self.limit == 0:
            return 0
        return min((self.spent / self.limit) * 100, 100)

    @property
    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.spent > self.limit

    def __str__(self):
        return f"{self.category.name} - {self.limit} ({self.period})"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('budget_warning', 'Budget Warning'),
        ('budget_exceeded', 'Budget Exceeded'),
        ('transaction_alert', 'Transaction Alert'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
