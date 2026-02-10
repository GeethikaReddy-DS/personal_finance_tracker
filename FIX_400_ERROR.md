# Fix 400 Bad Request Error on Render

## Problem
Your app is deployed but showing "400 Bad Request" when you visit `https://personal-finance-tracker-yi58.onrender.com`

## Cause
Django's `ALLOWED_HOSTS` security check is rejecting requests because the Render domain is not in the allowed hosts list.

## Solution

### Step 1: Add ALLOWED_HOSTS Environment Variable

1. Go to https://dashboard.render.com
2. Click on your Web Service: **personal-finance-tracker**
3. Click **"Environment"** in the left sidebar
4. Click **"Add Environment Variable"**
5. Add:
   ```
   Key: ALLOWED_HOSTS
   Value: personal-finance-tracker-yi58.onrender.com
   ```
6. Click **"Save Changes"**
7. Render will **automatically redeploy** (wait 2-3 minutes)

### Step 2: Verify Fixed

After redeploy completes:
1. Visit: https://personal-finance-tracker-yi58.onrender.com
2. You should see the login page (not 400 error)
3. Try these URLs:
   - `/login/` - Login page
   - `/register/` - Registration page
   - `/dashboard/` - Dashboard (after login)

### Step 3: Create Your First Account

1. Go to `/register/`
2. Fill in:
   - Username
   - Email
   - Password (twice)
3. Click "Register"
4. Login with your credentials
5. Categories auto-created via signals!

---

## Current Environment Variables Needed

Make sure you have ALL these set in Render:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Your generated key |
| `DEBUG` | `0` |
| `ALLOWED_HOSTS` | `personal-finance-tracker-yi58.onrender.com` ← **ADD THIS** |
| `DATABASE_URL` | Auto-set by Render ✅ |

Optional (for Django admin):
| Variable | Value |
|----------|-------|
| `DJANGO_SUPERUSER_USERNAME` | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Your secure password |

---

## After Fix

Access your app at:
- **Main App**: https://personal-finance-tracker-yi58.onrender.com/login/
- **Django Admin** (if superuser created): https://personal-finance-tracker-yi58.onrender.com/admin/

---

## Quick Check: Is `ALLOWED_HOSTS` Set?

Look in Render Environment tab. You should see:
```
ALLOWED_HOSTS = personal-finance-tracker-yi58.onrender.com
```

If missing → **Add it now**
If present → **Check the value matches your URL exactly** (no https://, no trailing slash)

---

That's it! Once you add `ALLOWED_HOSTS`, the 400 error will disappear and you'll see your beautiful finance tracker app! 🚀
