from django.contrib import admin
from .models import Budget, Notification


class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'limit', 'spent', 'period', 'is_over_budget']
    list_filter = ['period', 'category__type', 'created_at']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['created_at', 'updated_at']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']


admin.site.register(Budget, BudgetAdmin)
admin.site.register(Notification, NotificationAdmin)
