# Render vs Vercel for Django

## Quick Comparison

| Feature | Render | Vercel |
|---------|--------|--------|
| **Django Support** | ✅ Native | ❌ Serverless only (not ideal) |
| **PostgreSQL** | ✅ Built-in | ❌ Need external DB service |
| **Setup Time** | 5-10 min | 30+ min (complex) |
| **Free Tier** | ✅ Yes | ✅ Yes |
| **Recommended** | ✅ **YES** | ⚠️ Not recommended for Django |

---

## Recommendation: **USE RENDER**

Render is designed for traditional Django apps. Vercel is for serverless functions (Node.js, Python functions, etc.) and requires significant code restructuring.

**For this assignment, deploy on Render (see DEPLOY_RENDER.md).**

---

## If You Really Want Vercel

Vercel doesn't directly support Django long-running servers. You'd need to:
1. Convert your app to use Vercel's serverless functions (major refactor)
2. Use an external PostgreSQL service (e.g., Supabase, Neon)
3. Deploy each Django view as a separate function

**This is complex and NOT recommended for your assignment.**

---

## Best Path Forward

1. **Use Render** (follow DEPLOY_RENDER.md)
2. **Live in 10-15 minutes**
3. **No app restructuring needed**
4. **Works perfectly for Django**

---

## See Also
- Render docs: https://render.com/docs/deploy-django
- Why not Vercel for Django: https://vercel.com/guides/deploying-django-with-vercel (note: requires serverless refactoring)
