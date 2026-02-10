# Render Deployment Guide (Recommended for Django)

## Why Render?
- **Free tier**: Yes (limited but works for demos)
- **PostgreSQL**: Free tier available
- **Django support**: Native support (no serverless complications)
- **Custom domains**: Free SSL included
- **Simplicity**: UI is straightforward

## Step-by-Step Deployment

### 1. Push Code to GitHub

Make sure your repo is on GitHub (public or private).

```powershell
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repo

### 3. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Select your repository
3. Fill in:
   - **Name**: `personal-finance-tracker` (or your choice)
   - **Environment**: Select `Python 3`
   - **Build Command**: `pip install -r requirements-prod.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn config.wsgi`
   - **Plan**: Leave as "Free" (or upgrade to paid)

### 4. Add Environment Variables

1. In Render dashboard, scroll to **"Environment"** section
2. Add these variables one by one:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `SECRET_KEY` | `your-secret-key-here` | Generate: `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `0` | Must be `0` for production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your Render app name |
| `DATABASE_URL` | *(auto-set by Render)* | Renders sets this automatically when you add Postgres |
| `PYTHON_VERSION` | `3.12.4` | Optional, specifies Python version |

### 5. Add PostgreSQL Database

1. In the same project, click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `personal-finance-db`
   - **Database**: `finance_db`
   - **User**: `postgres`
   - **Region**: Same as your Web Service (for performance)
   - **Plan**: "Free" tier

3. Click **"Create Database"**

4. **Important**: Render will automatically add `DATABASE_URL` to your Web Service environment. No manual action needed.

### 6. Deploy

1. Click **"Deploy"** button (or Render will auto-deploy when you push to main)
2. Monitor the deploy progress in the **"Events"** tab
3. Wait for the build to complete (5-10 minutes on first deploy)

### 7. Run Migrations

1. Once deploy is successful, click **"Shell"** tab in Render dashboard
2. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
3. Create a superuser account for Django admin

### 8. Access Your App

Your app is now live at: `https://your-app-name.onrender.com`

---

## Full Environment Variables Summary

```
SECRET_KEY=django-insecure-YOUR-GENERATED-KEY-HERE
DEBUG=0
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgres://user:password@host:5432/finance_db
PYTHON_VERSION=3.12.4
```

---

## Database Setup (Auto by Render)

When you create a PostgreSQL instance on Render:
- **Hostname**: `dpg-xxxxx.onrender.com`
- **Port**: `5432`
- **Database**: `finance_db`
- **User**: `postgres`
- **Password**: Auto-generated (shown once)

The `DATABASE_URL` environment variable is **automatically set** and passed to your Django app via `dj-database-url` in `settings.py`.

**No manual database URL construction needed!**

---

## Common Issues & Fixes

**Issue: "No modules named 'whitenoise'**
- Fix: Ensure `requirements-prod.txt` is committed and pushed to GitHub

**Issue: `DisallowedHost` error when visiting app**
- Fix: Update `ALLOWED_HOSTS` env var to match your Render domain exactly

**Issue: 502 Bad Gateway**
- Fix: Check logs in Render → "Events" tab. Usually a startup error. Common causes:
  - Missing migration: Run `heroku run python manage.py migrate` equivalent in Shell
  - incorrect SECRET_KEY

**Issue: Static files (CSS/images) not loading**
- Fix: Build command already includes `collectstatic`. If still broken, run in Shell:
  ```bash
  python manage.py collectstatic --noinput
  ```

**Issue: Database won't connect**
- Fix: Render sets `DATABASE_URL` automatically. Just verify it exists in environment vars.

---

## After Deployment

1. **Register a user**: Visit `/register/` on your live app
2. **Add categories**: User gets defaults via Django signal on signup
3. **Create transactions**: Start tracking
4. **View reports**: Dashboard auto-calculated

---

## Upgrade to Paid (Optional)

If free tier runs out or you want better performance:
- Web Service: ~\$7/month
- PostgreSQL: ~\$7/month

---

## Next Steps

After deployment is live:
1. Get your live URL: `https://your-app-name.onrender.com`
2. Update submission with:
   - **Deployed Demo Link**: Your live URL
   - **GitHub Repo**: Your private repo link
   - **Loom walkthrough**: Upcoming
