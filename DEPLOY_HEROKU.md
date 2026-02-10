# Heroku Deployment Guide

## Prerequisites

1. **Heroku Account**: Sign up at https://dashboard.heroku.com
2. **Heroku CLI**: Install from https://devcenter.heroku.com/articles/heroku-cli
3. **Git**: Ensure repo is initialized and committed

## Deployment Steps

### 1. Install Heroku CLI & Login

```powershell
# Install Heroku CLI
choco install heroku-cli
# OR download from: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login
```

### 2. Create Heroku App

```powershell
# Create app (replace 'my-finance-tracker' with your desired app name)
heroku create my-finance-tracker

# Add Heroku Git remote
heroku git:remote -a my-finance-tracker
```

### 3. Add PostgreSQL Database

```powershell
# Add Postgres add-on (free tier: `hobby-dev`)
heroku addons:create heroku-postgresql:hobby-dev -a my-finance-tracker
```

### 4. Set Environment Variables (Config Vars)

```powershell
# Generate a new Django SECRET_KEY (replace with a real key from Django shell)
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Set config variables
heroku config:set SECRET_KEY="your-generated-secret-key" -a my-finance-tracker
heroku config:set DEBUG="0" -a my-finance-tracker
heroku config:set ALLOWED_HOSTS="my-finance-tracker.herokuapp.com" -a my-finance-tracker
```

### 5. Deploy

```powershell
# Commit all changes
git add .
git commit -m "Prepare for Heroku deployment"

# Deploy to Heroku
git push heroku main
# (if branch is 'master' instead: git push heroku master)
```

### 6. Run Migrations

```powershell
# Run Django migrations on Heroku
heroku run python manage.py migrate -a my-finance-tracker

# Collect static files (optional, WhiteNoise handles this)
heroku run python manage.py collectstatic --noinput -a my-finance-tracker

# Create superuser (optional, for Django admin)
heroku run python manage.py createsuperuser -a my-finance-tracker
```

### 7. Open App

```powershell
# Open in browser
heroku open -a my-finance-tracker
```

## Verify Deployment

```powershell
# Check logs
heroku logs --tail -a my-finance-tracker

# Check config vars
heroku config -a my-finance-tracker

# Check dyno status
heroku ps -a my-finance-tracker
```

## Common Issues & Fixes

**Issue: `ModuleNotFoundError: No module named 'whitenoise'`**
- Fix: Heroku will auto-install from `requirements.txt`; ensure it's committed to git.

**Issue: `DisallowedHost` error**
- Fix: Update `ALLOWED_HOSTS` config var:
  ```powershell
  heroku config:set ALLOWED_HOSTS="my-finance-tracker.herokuapp.com,www.my-finance-tracker.herokuapp.com"
  ```

**Issue: Database migrations don't run**
- Fix: Manually run:
  ```powershell
  heroku run python manage.py migrate
  ```

**Issue: Static files not loading**
- Fix: Already handled by WhiteNoise; if images/CSS missing:
  ```powershell
  heroku run python manage.py collectstatic --noinput
  ```

## Post-Deployment

1. **Register a User**: Go to `/register/` and create an account.
2. **Create Categories**: Users get default categories on signup via signals.
3. **Add Transactions**: Start tracking expenses/income.
4. **View Dashboard**: See summary, reports, budgets.

## Useful Heroku Commands

```powershell
# Restart app
heroku restart -a my-finance-tracker

# Scale dynos (free tier = 1)
heroku ps:scale web=1 -a my-finance-tracker

# Run Django shell
heroku run python manage.py shell -a my-finance-tracker

# Delete app
heroku apps:destroy my-finance-tracker
```

## Custom Domain (Optional)

```powershell
# Add custom domain
heroku domains:add www.yourdomain.com -a my-finance-tracker

# Check DNS setup instructions
heroku domains -a my-finance-tracker
```

## Production Security Checklist

- [ ] SECRET_KEY is unique and strong
- [ ] DEBUG = 0
- [ ] ALLOWED_HOSTS set to your domain
- [ ] HTTPS enabled (Heroku provides free SSL)
- [ ] SESSION_COOKIE_SECURE = True in settings (for HTTPS)
- [ ] CSRF_COOKIE_SECURE = True in settings (for HTTPS)

## Next Steps

After deployment, update your submission with:
- **Deployed Demo Link**: `https://my-finance-tracker.herokuapp.com`
- **GitHub Repo**: Your private repo link
- Loom walkthrough video

---

For more info: https://devcenter.heroku.com/articles/getting-started-with-django
