# Render Deployment - Super Quick Start

## 5-Minute Summary

1. **Push code to GitHub**
   ```powershell
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Go to https://render.com** → Sign up with GitHub

3. **Click "New +" → "Web Service"**
   - Select your repo
   - **Name**: `personal-finance-tracker`
   - **Build Command**: `pip install -r requirements-prod.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn config.wsgi`
   - Click "Create Web Service"

4. **Add Environment Variables** (while deployment is running):
   ```
   SECRET_KEY = [generate: python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
   DEBUG = 0
   ALLOWED_HOSTS = your-app-name.onrender.com
   ```

5. **Add PostgreSQL** (New + → PostgreSQL)
   - Same name: `personal-finance-db`
   - Region: Same as Web Service
   - Database URL auto-added to Web Service

6. **Wait for deployment** (5-10 minutes)
   - Migrations run automatically during build (see build command above)
   - No Shell needed!

7. **Visit**: `https://your-app-name.onrender.com`
   - Go to `/register/` and create your first user account
   - Categories are auto-created via Django signals
   - Start adding transactions!

**Note**: Admin access is optional. If you need Django admin, create a superuser locally with same credentials, or use the `/register/` page and manually promote the user to staff via database tools.

---

## All Environment Variables Needed

| Name | Value |
|------|-------|
| `SECRET_KEY` | Copy output from: `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `0` |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `DATABASE_URL` | Auto-set by Render (no action needed) |

---

## Database

**Render handles it automatically:**
- You create a PostgreSQL instance
- Render injects `DATABASE_URL` env var
- Your Django app reads it (via `dj-database-url`)
- **No manual connection string needed**

---

## Done? Then:

1. **Live URL**: `https://your-app-name.onrender.com`
2. **Register**: Create account at `/register/`
3. **Add categories & transactions**: Start using the app
4. **For submission**: Note your live URL for the Google Form
