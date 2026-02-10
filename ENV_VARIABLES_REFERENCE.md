# Environment Variables Reference

## For Render Deployment

Add these in **Render Dashboard → Environment**:

### Required Variables

| Variable | Value | How to Get |
|----------|-------|-----------|
| `SECRET_KEY` | `django-insecure-xxxxx...` | Run: `python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `0` | Always `0` for production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Use your Render app name (shown in Render dashboard) |

### Auto-Set by Render

| Variable | Set By | Notes |
|----------|--------|-------|
| `DATABASE_URL` | Render (when you add PostgreSQL) | Do NOT set manually; Render injects it automatically after you create a PostgreSQL instance |

---

## How to Generate SECRET_KEY

### Option 1: On Windows (PowerShell)
```powershell
python manage.py shell
```

Then paste this code:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copy the output (looks like: `django-insecure-abc123...xyz`)

### Option 2: One-liner
```powershell
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Setup (Render)

### Step 1: Create PostgreSQL
1. In Render, click **"New +"** → **"PostgreSQL"**
2. Fill in:
   - **Name**: `personal-finance-db`
   - **Database**: `finance_db`
   - **User**: `postgres` (auto-generated)
   - **Region**: Same as Web Service
   - **Plan**: Free
3. Click **"Create Database"**

### Step 2: Auto Connection
- Render automatically sets `DATABASE_URL` in your Web Service environment
- Your Django app reads it via `dj_database_url.config()`
- **No manual setup needed!**

### Step 3: Run Migrations
After deployment succeeds:
1. Click **"Shell"** tab in Render
2. Run:
   ```bash
   python manage.py migrate
   ```

---

## Complete Environment Variables List

Paste all these into Render (replace values):

```
SECRET_KEY=django-insecure-YOUR_GENERATED_KEY_HERE
DEBUG=0
ALLOWED_HOSTS=your-app-name.onrender.com
PYTHON_VERSION=3.12.4
```

**Note**: `DATABASE_URL` is auto-set by Render when you add PostgreSQL. Do NOT add it manually.

---

## Local Development (`.env` file - optional)

If you want to test with these env vars locally, create `.env` in project root:

```
SECRET_KEY=django-insecure-dev-key
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

Then install `python-dotenv`:
```powershell
pip install python-dotenv
```

And update settings.py (already supported in our config).

---

## Verification

### Check if Render has DATABASE_URL set:
1. Go to Render Dashboard
2. Click your Web Service
3. Scroll to **"Environment"**
4. Look for `DATABASE_URL` (should appear after PostgreSQL is created)

### Test locally:
```powershell
$env:SECRET_KEY="test-key"
$env:DEBUG="0"
$env:ALLOWED_HOSTS="127.0.0.1"
python manage.py check
```

---

## Troubleshooting

**"DisallowedHost" error**
- Fix: Update `ALLOWED_HOSTS` to match your Render domain exactly

**"Connection refused" on database**
- Fix: Ensure PostgreSQL instance is created and running
- Check `DATABASE_URL` exists in environment

**"ModuleNotFoundError"**
- Fix: Ensure all packages in `requirements-prod.txt` are committed to GitHub

---

## After Getting Live

1. Visit `https://your-app-name.onrender.com`
2. Register a user
3. Categories auto-created via signal
4. Create transactions and explore

This is all you need! 🚀
