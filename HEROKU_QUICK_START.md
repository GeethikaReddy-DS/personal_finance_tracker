# Quick Heroku Deployment – Copy/Paste Commands

## Step 1: Login to Heroku
```powershell
heroku login
```

## Step 2: Create App & Database
```powershell
heroku create my-finance-tracker
heroku addons:create heroku-postgresql:hobby-dev -a my-finance-tracker
```

## Step 3: Set Environment Variables
```powershell
# First, generate a SECRET_KEY:
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy the output, then run:
heroku config:set SECRET_KEY="paste-your-key-here" DEBUG="0" ALLOWED_HOSTS="my-finance-tracker.herokuapp.com" -a my-finance-tracker
```

## Step 4: Commit & Deploy
```powershell
git add .
git commit -m "Ready for Heroku"
git push heroku main
```

## Step 5: Setup Database & Admin
```powershell
heroku run python manage.py migrate -a my-finance-tracker
heroku run python manage.py createsuperuser -a my-finance-tracker
```

## Step 6: Visit Your App
```powershell
heroku open -a my-finance-tracker
```

## All-in-One Script (after `heroku login`)
```powershell
$APP_NAME = "my-finance-tracker"

# Create app & DB
heroku create $APP_NAME
heroku addons:create heroku-postgresql:hobby-dev -a $APP_NAME
heroku git:remote -a $APP_NAME

# Generate SECRET_KEY (copy output manually)
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# MANUALLY paste SECRET_KEY in next command (replace YOUR_KEY):
$SECRET_KEY = "YOUR_KEY_FROM_ABOVE"
heroku config:set SECRET_KEY="$SECRET_KEY" DEBUG="0" ALLOWED_HOSTS="$APP_NAME.herokuapp.com" -a $APP_NAME

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Migrate & create superuser
heroku run python manage.py migrate -a $APP_NAME
heroku run python manage.py createsuperuser -a $APP_NAME

# Open browser
heroku open -a $APP_NAME
```

---

**Your Live App URL**: `https://my-finance-tracker.herokuapp.com`

**Next**: Test login, register a user, create categories, and add transactions!
