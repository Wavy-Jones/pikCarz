# 🚀 Deploy to Vercel - Quick Guide

## Why Vercel Works for You

Since you already deployed AuraBook to Vercel, this will be familiar! Same process.

**Pros:**
- ✅ You know it already
- ✅ Free tier (plenty for MVP)
- ✅ PostgreSQL included (Vercel Postgres = Neon)
- ✅ Fast deployment
- ✅ Auto HTTPS
- ✅ Easy environment variables

**Cons:**
- ⚠️ Serverless = cold starts (2-3 second delay if no recent traffic)
- ⚠️ 10-second timeout on free tier
- ⚠️ Need connection pooling for database

**Verdict:** Perfect for MVP! You can migrate to Railway later if you need always-warm servers.

---

## 📋 Prerequisites

1. ✅ Vercel account (you already have one from AuraBook)
2. ✅ Vercel CLI installed: `npm i -g vercel`

---

## 🗄️ Step 1: Setup PostgreSQL (5 mins)

### Option A: Vercel Postgres (Easiest)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Storage → Create Database → Postgres
3. Name it: `pikcarz-db`
4. Copy the connection strings (you'll use `POSTGRES_PRISMA_URL`)

### Option B: Neon.tech (Also Free)

1. Go to [neon.tech](https://neon.tech)
2. Sign up → Create Project → Name it `pikcarz`
3. Copy the connection string

---

## ⚙️ Step 2: Deploy Backend to Vercel (2 mins)

```bash
cd C:\Repos\PikCarz\backend

# Login to Vercel (if not already)
vercel login

# Deploy!
vercel
```

**During deployment, answer:**
- Set up and deploy? **Y**
- Which scope? **Your account**
- Link to existing project? **N**
- Project name? **pikcarz-backend**
- Directory? **./backend** (or just press Enter)
- Override settings? **N**

**Vercel will deploy and give you a URL like:**
`https://pikcarz-backend.vercel.app`

---

## 🔐 Step 3: Set Environment Variables (3 mins)

### On Vercel Dashboard:

1. Go to your project → Settings → Environment Variables
2. Add these one by one:

```env
# Database (from Step 1)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
FRONTEND_URL=https://wavy-jones.github.io/pikCarz

# Cloudinary (get from cloudinary.com - free account)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# PayFast (get from payfast.co.za)
PAYFAST_MERCHANT_ID=your-merchant-id
PAYFAST_MERCHANT_KEY=your-merchant-key
PAYFAST_PASSPHRASE=your-passphrase
PAYFAST_MODE=sandbox

# Admin
ADMIN_EMAIL=admin@pikcarz.co.za
ADMIN_PASSWORD=change-this-in-production

# App
APP_NAME=pikCarz API
DEBUG=False
```

3. Click **Save**
4. Go to Deployments → Click the 3 dots on latest → **Redeploy**

---

## ✅ Step 4: Test It Works

```bash
# Test health check
curl https://pikcarz-backend.vercel.app/

# Should return:
# {"status":"online","app":"pikCarz API","version":"1.0.0"}

# Test API docs
# Open in browser: https://pikcarz-backend.vercel.app/docs
```

---

## 🔄 Step 5: Update Frontend to Use Live API

Later, when connecting frontend, you'll update the API URLs to:
```javascript
const API_BASE_URL = 'https://pikcarz-backend.vercel.app';
```

---

## 🛠️ Local Development (Same as Before)

```bash
cd backend

# Install
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Access at http://localhost:8000
```

---

## 📊 Vercel vs Railway Quick Comparison

| Task | Vercel (Familiar) | Railway (New) |
|------|------------------|---------------|
| **Deploy** | `vercel` | `railway up` |
| **Logs** | Dashboard or `vercel logs` | `railway logs` |
| **Database** | Vercel Postgres (Neon) | Built-in Postgres |
| **You Know It?** | ✅ Yes (AuraBook) | ❌ No |
| **Cold Start** | Yes (~2s first request) | No (always warm) |
| **Free Tier** | ✅ Generous | ✅ $5 credit/month |

**Recommendation:** Start with Vercel since you know it. If cold starts become an issue later (they won't for MVP), migrate to Railway in 10 minutes.

---

## 🐛 Common Vercel Issues & Fixes

### "Module not found" error
```bash
# Make sure requirements.txt is complete
pip freeze > requirements.txt
git add . && git commit -m "update deps" && git push
vercel --prod
```

### "Database connection failed"
- Make sure `DATABASE_URL` includes `?sslmode=require` at the end
- Check Vercel Postgres is running (dashboard → storage)

### "Cold start too slow"
- This is normal for serverless (first request after idle)
- Users won't notice on MVP
- If it's a problem later: migrate to Railway

### "Can't import app.main"
- Make sure you're deploying from the `backend` folder
- Check `vercel.json` is in the backend folder

---

## 🚀 Production Checklist (Monday Morning)

Before going live:
- [ ] Environment variables set on Vercel
- [ ] Database migrations run (tables created)
- [ ] Test registration works: `POST /api/auth/register`
- [ ] Test login works: `POST /api/auth/login`
- [ ] API docs accessible: `/docs`
- [ ] PayFast mode set to `live` (not sandbox)
- [ ] FRONTEND_URL updated to production URL

---

## 💡 Pro Tips

**Auto-deploy on Git Push:**
```bash
# Link to GitHub
vercel --prod

# Now every push to main = auto-deploy!
```

**View Logs:**
```bash
vercel logs
# or visit dashboard → your-project → Logs
```

**Redeploy:**
```bash
vercel --prod
```

---

**Next Step:** Once backend is deployed to Vercel, we'll build the remaining API endpoints (vehicles, subscriptions, payments) and you're live! 🎯
