from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    # Reports
    path('reports/monthly/', views.report_monthly, name='report_monthly'),
    path('reports/yearly/', views.report_yearly, name='report_yearly'),
    path('reports/category/', views.report_category, name='report_category'),

    # API endpoints
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    path('api/monthly-trend/', views.api_monthly_trend, name='api_monthly_trend'),
]
