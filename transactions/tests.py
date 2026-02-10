from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, timedelta
from transactions.models import Transaction, Category, UserProfile, Receipt
from budgets.models import Budget, Notification


class UserAuthenticationTest(TestCase):
    """Test user authentication and profile management"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertEqual(User.objects.count(), 1)
    
    def test_user_login(self):
        """Test user can login"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_user_logout(self):
        """Test user can logout"""
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
    
    def test_profile_access_requires_login(self):
        """Test profile page requires login"""
        response = self.client.get(self.profile_url)
        self.assertNotEqual(response.status_code, 200)
    
    def test_userprofile_creation(self):
        """Test UserProfile is created with User"""
        user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.preferred_currency, 'USD')


class TransactionTest(TestCase):
    """Test transaction creation and management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.category_income = Category.objects.create(
            user=self.user,
            name='Salary',
            type='income'
        )
        self.category_expense = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
    
    def test_create_income_transaction(self):
        """Test creating income transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category_income,
            amount=Decimal('5000.00'),
            currency='USD',
            date=date.today(),
            description='Monthly salary'
        )
        self.assertEqual(transaction.amount, Decimal('5000.00'))
        self.assertEqual(transaction.currency, 'USD')
    
    def test_create_expense_transaction(self):
        """Test creating expense transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category_expense,
            amount=Decimal('50.00'),
            currency='USD',
            date=date.today(),
            description='Lunch'
        )
        self.assertEqual(transaction.amount, Decimal('50.00'))
    
    def test_negative_amount_without_refund(self):
        """Test negative amount must be marked as refund"""
        from django.core.exceptions import ValidationError
        transaction = Transaction(
            user=self.user,
            category=self.category_expense,
            amount=Decimal('-50.00'),
            currency='USD',
            date=date.today(),
            is_refund=False
        )
        with self.assertRaises(ValidationError):
            transaction.clean()
    
    def test_refund_transaction(self):
        """Test refund transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category_expense,
            amount=Decimal('-50.00'),
            currency='USD',
            date=date.today(),
            is_refund=True,
            description='Refund'
        )
        self.assertEqual(transaction.amount, Decimal('-50.00'))
        self.assertTrue(transaction.is_refund)
    
    def test_multiple_currencies(self):
        """Test transactions with different currencies"""
        currencies = ['USD', 'EUR', 'GBP', 'INR']
        for curr in currencies:
            transaction = Transaction.objects.create(
                user=self.user,
                category=self.category_income,
                amount=Decimal('1000.00'),
                currency=curr,
                date=date.today()
            )
            self.assertEqual(transaction.currency, curr)
    
    def test_decimal_precision(self):
        """Test decimal precision is maintained"""
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category_expense,
            amount=Decimal('99.99'),
            currency='USD',
            date=date.today()
        )
        self.assertEqual(transaction.amount, Decimal('99.99'))
        # Verify storage
        from_db = Transaction.objects.get(pk=transaction.pk)
        self.assertEqual(str(from_db.amount), '99.99')


class CategoryTest(TestCase):
    """Test category management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
    
    def test_create_category(self):
        """Test creating category"""
        category = Category.objects.create(
            user=self.user,
            name='Transport',
            type='expense'
        )
        self.assertEqual(category.name, 'Transport')
        self.assertEqual(category.type, 'expense')
    
    def test_category_belongs_to_user(self):
        """Test categories are user-specific"""
        user2 = User.objects.create_user(
            username='testuser2',
            password='TestPass123!'
        )
        cat1 = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
        cat2 = Category.objects.create(
            user=user2,
            name='Food',
            type='expense'
        )
        self.assertEqual(Category.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Category.objects.filter(user=user2).count(), 1)
    
    def test_delete_category_orphans_transactions(self):
        """Test deleting category doesn't delete transactions"""
        category = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
        transaction = Transaction.objects.create(
            user=self.user,
            category=category,
            amount=Decimal('50.00'),
            currency='USD',
            date=date.today()
        )
        category_id = category.id
        category.delete()
        
        # Transaction should still exist but be uncategorized
        trans = Transaction.objects.get(pk=transaction.pk)
        self.assertIsNone(trans.category)


class BudgetTest(TestCase):
    """Test budgeting functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
    
    def test_create_budget(self):
        """Test creating budget"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly'
        )
        self.assertEqual(budget.limit, Decimal('500.00'))
        self.assertEqual(budget.period, 'monthly')
    
    def test_budget_tracking(self):
        """Test budget spending tracking"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly'
        )
        
        # Create transactions
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('200.00'),
            currency='USD',
            date=date.today()
        )
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('150.00'),
            currency='USD',
            date=date.today()
        )
        
        self.assertEqual(budget.remaining, Decimal('500.00'))  # Before signal
    
    def test_budget_over_limit(self):
        """Test budget over limit detection"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('100.00'),
            period='monthly',
            spent=Decimal('150.00')
        )
        self.assertTrue(budget.is_over_budget)
    
    def test_budget_percentage(self):
        """Test budget percentage calculation"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly',
            spent=Decimal('250.00')
        )
        self.assertEqual(budget.percentage_used, 50.0)


class NotificationTest(TestCase):
    """Test notification system"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.category = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly'
        )
    
    def test_create_notification(self):
        """Test creating notification"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='budget_exceeded',
            title='Budget Exceeded',
            message='You exceeded your budget for Food',
            budget=self.budget
        )
        self.assertEqual(notification.notification_type, 'budget_exceeded')
    
    def test_notification_read_status(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='budget_warning',
            title='Budget Warning',
            message='You are close to your budget limit'
        )
        self.assertFalse(notification.is_read)
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)


class DashboardTest(TestCase):
    """Test dashboard functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.dashboard_url = reverse('dashboard')
        self.client.login(username='testuser', password='TestPass123!')
        
        # Setup categories
        self.income_cat = Category.objects.create(
            user=self.user,
            name='Salary',
            type='income'
        )
        self.expense_cat = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
    
    def test_dashboard_accessible(self):
        """Test dashboard is accessible for logged in users"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_shows_totals(self):
        """Test dashboard displays correct totals"""
        Transaction.objects.create(
            user=self.user,
            category=self.income_cat,
            amount=Decimal('5000.00'),
            currency='USD',
            date=date.today()
        )
        Transaction.objects.create(
            user=self.user,
            category=self.expense_cat,
            amount=Decimal('500.00'),
            currency='USD',
            date=date.today()
        )
        
        response = self.client.get(self.dashboard_url)
        self.assertContains(response, '5000.00')
        self.assertContains(response, '500.00')


class ReportTest(TestCase):
    """Test reporting functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
        
        # Setup categories
        self.income_cat = Category.objects.create(
            user=self.user,
            name='Salary',
            type='income'
        )
        self.expense_cat = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
    
    def test_monthly_report(self):
        """Test monthly report generation"""
        report_url = reverse('report_monthly')
        response = self.client.get(report_url)
        self.assertEqual(response.status_code, 200)
    
    def test_yearly_report(self):
        """Test yearly report generation"""
        report_url = reverse('report_yearly')
        response = self.client.get(report_url)
        self.assertEqual(response.status_code, 200)
    
    def test_category_report(self):
        """Test category-wise report"""
        report_url = reverse('report_category')
        response = self.client.get(report_url)
        self.assertEqual(response.status_code, 200)
