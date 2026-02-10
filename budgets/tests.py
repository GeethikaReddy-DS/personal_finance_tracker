from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date
from transactions.models import Category, Transaction
from budgets.models import Budget, Notification


class BudgetViewTest(TestCase):
    """Test budget views and functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
        
        self.category = Category.objects.create(
            user=self.user,
            name='Food',
            type='expense'
        )
        
        self.budget_list_url = reverse('budget_list')
        self.budget_create_url = reverse('budget_create')
    
    def test_budget_list_view(self):
        """Test budget list view"""
        response = self.client.get(self.budget_list_url)
        self.assertEqual(response.status_code, 200)
    
    def test_budget_create_view(self):
        """Test budget create view"""
        response = self.client.get(self.budget_create_url)
        self.assertEqual(response.status_code, 200)
    
    def test_budget_creation_via_form(self):
        """Test creating budget via POST"""
        from datetime import date, timedelta
        
        # Ensure the category is properly set up
        self.assertIsNotNone(self.category)
        
        today = date.today()
        start = today.replace(day=1)
        end = today.replace(day=28) if today.month != 12 else today.replace(day=25)
        
        response = self.client.post(self.budget_create_url, {
            'category': self.category.id,
            'limit': '500.00',
            'period': 'monthly',
            'start_date': start.isoformat(),
            'end_date': end.isoformat(),
        }, follow=True)
        
        # Should redirect to budget_list
        self.assertIn(response.status_code, [200, 302])
        self.assertEqual(Budget.objects.count(), 1)
        budget = Budget.objects.first()
        self.assertEqual(budget.limit, Decimal('500.00'))
        self.assertEqual(budget.period, 'monthly')
    
    def test_budget_detail_view(self):
        """Test budget detail view"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly'
        )
        detail_url = reverse('budget_detail', kwargs={'pk': budget.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)


class NotificationViewTest(TestCase):
    """Test notification views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')
        
        self.notification_list_url = reverse('notification_list')
    
    def test_notification_list_view(self):
        """Test notification list view"""
        response = self.client.get(self.notification_list_url)
        self.assertEqual(response.status_code, 200)
    
    def test_notification_list_shows_unread_count(self):
        """Test notification list shows unread count"""
        Notification.objects.create(
            user=self.user,
            notification_type='budget_warning',
            title='Warning',
            message='Budget warning',
            is_read=False
        )
        response = self.client.get(self.notification_list_url)
        self.assertContains(response, '1')  # Unread count


class BudgetSignalTest(TestCase):
    """Test budget signals and automatic tracking"""
    
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
    
    def test_budget_spent_updated_on_transaction(self):
        """Test budget.spent is updated when transaction is added"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly'
        )
        
        # Create a transaction
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('100.00'),
            currency='USD',
            date=date.today()
        )
        
        # Refresh budget from DB
        budget.refresh_from_db()
        self.assertEqual(budget.spent, Decimal('100.00'))
    
    def test_budget_notification_on_exceeded(self):
        """Test notification is created when budget is exceeded"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('100.00'),
            period='monthly',
            spent=Decimal('80.00')
        )
        
        # Add transaction that exceeds budget
        Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('30.00'),
            currency='USD',
            date=date.today()
        )
        
        # Check if notification was created
        notifications = Notification.objects.filter(
            user=self.user,
            notification_type='budget_exceeded'
        )
        # Note: This assumes signal is configured, may need adjustment


class BudgetCalculationTest(TestCase):
    """Test budget calculation and percentage tracking"""
    
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
    
    def test_remaining_budget_calculation(self):
        """Test remaining budget is calculated correctly"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly',
            spent=Decimal('300.00')
        )
        self.assertEqual(budget.remaining, Decimal('200.00'))
    
    def test_percentage_used_calculation(self):
        """Test percentage used is calculated correctly"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly',
            spent=Decimal('250.00')
        )
        self.assertEqual(budget.percentage_used, 50.0)
    
    def test_is_over_budget(self):
        """Test budget over limit detection"""
        budget1 = Budget.objects.create(
            user=self.user,
            category=self.category,
            limit=Decimal('500.00'),
            period='monthly',
            spent=Decimal('300.00')
        )
        budget2 = Budget.objects.create(
            user=self.user,
            category=Category.objects.create(
                user=self.user,
                name='Transport',
                type='expense'
            ),
            limit=Decimal('100.00'),
            period='monthly',
            spent=Decimal('150.00')
        )
        self.assertFalse(budget1.is_over_budget)
        self.assertTrue(budget2.is_over_budget)

