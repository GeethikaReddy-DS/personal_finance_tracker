from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    preferred_currency = models.CharField(
        max_length=3, 
        default='USD',
        choices=[
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
            ('GBP', 'British Pound'),
            ('INR', 'Indian Rupee'),
            ('JPY', 'Japanese Yen'),
            ('AUD', 'Australian Dollar'),
            ('CAD', 'Canadian Dollar'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        unique_together = ('user', 'name', 'type')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


class Receipt(models.Model):
    UPLOAD_TO = 'receipts/%Y/%m/'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=UPLOAD_TO)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Receipt - {self.file_name}"
    
    def save(self, *args, **kwargs):
        self.file_name = self.file.name
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-uploaded_at']


class Transaction(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('INR', 'Indian Rupee'),
        ('JPY', 'Japanese Yen'),
        ('AUD', 'Australian Dollar'),
        ('CAD', 'Canadian Dollar'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=3, 
        default='USD',
        choices=CURRENCY_CHOICES
    )
    date = models.DateField()
    description = models.TextField(blank=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_refund = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]

    def clean(self):
        if self.amount < 0 and not self.is_refund:
            raise ValidationError("Amount cannot be negative unless marked as a refund")
        if self.category and self.category.user != self.user:
            raise ValidationError("Category must belong to the same user")

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency}"
