# Personal Finance Tracker

A comprehensive Django-based web application for managing personal finances, tracking income, expenses, and investments with reporting and budgeting features.

## Features

### ✅ Day 1-2: Basic Functionality
- **User Authentication**: Register, login, logout, and profile management
- **Database Structure**: Well-defined models for users, transactions, categories, budgets
- **Transaction Management**: Add, edit, delete transactions with support for:
  - Multiple expense/income categories
  - Refund handling
  - Receipt uploads
  - Multiple currencies
  - Decimal precision handling
- **Dashboard**: Visual overview with charts showing:
  - Monthly income vs expenses
  - Savings summary
  - Budget warnings
  - Recent transactions
- **Reporting**:
  - Monthly income vs expenses reports
  - Yearly trend analysis
  - Category-wise spending breakdown
- **Budgeting**: Set monthly/yearly budget goals with:
  - Progress tracking
  - Budget overrun notifications
  - Spending visualization

### ✅ Day 3: Additional Features
- **Multiple Currencies**: Support for USD, EUR, GBP, INR, JPY, AUD, CAD
- **Receipt Uploading**: Upload and store receipts for transactions (PDF, JPG, PNG)
- **Notification System**:  
  - Budget warning notifications
  - Budget exceeded alerts
  - Admin dashboard for managing notifications
- **User Preferences**: Set preferred currency

### 🔄 Day 4: Deployment Ready
- Production-ready Django settings
- Database configuration for both SQLite and PostgreSQL
- Static and media file handling
- CORS support
- Error logging

### 🧪 Day 5: Testing
- Comprehensive form validation
- Exception handling for edge cases
- Permission-based access control

## Technology Stack

- **Backend**: Django 6.0 + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: Bootstrap 4 + Chart.js
- **Forms**: Django Crispy Forms + Bootstrap 4
- **File Storage**: Django FileField
- **Authentication**: Django built-in auth + custom signals

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip or conda
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd personal_finance_tracker

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 3. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

## Project Structure

```
personal_finance_tracker/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── transactions/          # Transaction management app
│   ├── models.py         # Transaction, Category, Receipt models
│   ├── views.py          # Transaction views and API endpoints
│   ├── forms.py          # Transaction and filter forms
│   ├── signals.py        # Budget update signals
│   └── urls.py           # Transaction URLs
├── budgets/              # Budgeting app
│   ├── models.py         # Budget and Notification models
│   ├── views.py          # Budget management views
│   ├── forms.py          # Budget forms
│   └── urls.py           # Budget URLs
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard
│   ├── auth/             # Authentication templates
│   ├── transactions/     # Transaction templates
│   ├── categories/       # Category templates
│   ├── budgets/          # Budget templates
│   ├── reports/          # Report templates
│   └── notifications/    # Notification templates
├── media/                # Uploaded files (receipts)
├── logs/                 # Application logs
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Usage Guide

### 1. Creating an Account
- Click "Register" on the login page
- Fill in your details
- Confirm your account

### 2. Setting Up Categories
- Navigate to "Categories"
- Create categories for Income and Expense types
- Examples: Salary, Food, Transport, Entertainment, etc.

### 3. Recording Transactions
- Click "Add Transaction" on the dashboard
- Select category, amount, currency, and date
- Optionally upload a receipt
- Mark as refund if applicable

### 4. Managing Budgets
- Go to "Budgets"
- Set spending limits for expense categories
- Choose budget period (daily, weekly, monthly, yearly)
- Track spending against limits

### 5. Viewing Reports
- Access "Reports" menu for:
  - Monthly breakdown (income vs expenses by category)
  - Yearly trends (12-month analysis)
  - Category-wise spending reports

### 6. Managing Notifications
- View all budget alerts and notifications
- Mark as read to clear the unread badge

## API Endpoints

### Dashboard Data (for charts)
- `GET /api/dashboard-data/` - Monthly expense/income breakdown
- `GET /api/monthly-trend/?months=6` - Historical trend data

## Configuration

### Settings File (`config/settings.py`)

Key settings to customize:

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # or 'django.db.backends.postgresql'
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email (for future notifications)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # or SendGrid

# Currencies
Supported: USD, EUR, GBP, INR, JPY, AUD, CAD
```

## Security Considerations

For production deployment:

1. **Environment Variables**: Use `.env` file for sensitive data
2. **HTTPS**: Enable SSL/TLS
3. **CSRF Protection**: Already enabled
4. **SQL Injection**: Use Django ORM (no raw SQL)
5. **XSS Protection**: Templates use Django auto-escaping
6. **CORS**: Configure allowed origins

## Database Optimization

The application includes database indexes for:
- User + Date filtering on transactions
- User + Category filtering on transactions
- Unique constraints on categories and budgets

## Error Handling

- Form validation for all user inputs
- Proper exception handling for edge cases:
  - Negative amounts without refund marking
  - Decimal precision (2 decimal places maintained)
  - Budget overruns
  - Orphaned transactions when categories deleted

## Future Enhancements

- [ ] OAuth2 integration (Google, GitHub)
- [ ] Bank statement CSV/PDF import
- [ ] Anomaly detection for unusual spending
- [ ] Email notifications via SendGrid
- [ ] Data export (PDF, Excel)
- [ ] Mobile app
- [ ] Real-time notifications using Websockets
- [ ] AI-powered budgeting recommendations

## Troubleshooting

### Database Errors
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Static Files Issues
```bash
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a feature branch  (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues or questions, please create an issue in the repository or contact the development team.

## Deployment

### Development
```bash
python manage.py runserver
```

### Production
Use WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Platforms
- **Heroku**: Use Procfile and requirements.txt
- **DigitalOcean**: Use App Platform or Droplet
- **AWS**: Use Elastic Beanstalk or EC2
- **Render**: Connect GitHub repository

## Changelog

### Version 1.0.0 (Current)
- Initial release with core features
- Support for multiple currencies
- Receipt uploads
- Budget tracking
- Comprehensive reporting
- Responsive UI with Bootstrap
