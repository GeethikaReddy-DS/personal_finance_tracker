from django.contrib import admin
from .models import Category, Transaction, Receipt, UserProfile

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['name', 'user__username']


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'currency', 'date', 'is_refund']
    list_filter = ['currency', 'date', 'is_refund', 'category__type']
    search_fields = ['user__username', 'description', 'category__name']
    readonly_fields = ['created_at', 'updated_at']


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'user__username']
    readonly_fields = ['uploaded_at']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_currency', 'created_at']
    list_filter = ['preferred_currency']
    readonly_fields = ['created_at', 'updated_at']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Receipt, ReceiptAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

