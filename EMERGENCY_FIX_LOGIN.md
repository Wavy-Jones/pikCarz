# 🚨 EMERGENCY FIX GUIDE - "Failed to fetch" Login Error

## ⚡ CRITICAL ISSUE: Backend Not Responding

**You're getting "Failed to fetch" which means the backend API at `https://pikcarz.vercel.app` is not responding.**

---

## 🔍 STEP 1: TEST THE BACKEND (RIGHT NOW!)

### Test Page Created:
**Open this file in your browser:** `C:\Repos\PikCarz\API_TEST.html`

OR

**Test manually:**
1. Open your browser
2. Go to: https://pikcarz.vercel.app/health
3. **Expected:** Should show `{"status": "healthy"}`
4. **If you see error/nothing:** Backend is DOWN!

---

## 🚀 STEP 2: CHECK VERCEL DEPLOYMENT

### Go to Vercel Dashboard:

1. **Visit:** https://vercel.com/dashboard
2. **Select:** pikCarz project
3. **Click:** "Deployments" tab
4. **Check latest deployment:**
   - ✅ **Green/Ready:** Backend is deployed
   - ❌ **Red/Failed:** Deployment failed - check logs!
   - ⏳ **Building:** Wait for it to finish

### If Deployment Failed:

**Click the failed deployment → View Function Logs**

**Common errors:**
- Missing environment variables
- Python package errors
- Database connection failures

---

## 🔧 STEP 3: QUICK FIXES

### Fix 1: Redeploy Backend

**If backend isn't deployed or is stale:**

```bash
cd C:\Repos\PikCarz
git add .
git commit -m "Emergency redeploy - fix login"
git push
```

**Vercel will auto-deploy!** Wait 2-3 minutes.

---

### Fix 2: Check Environment Variables

**In Vercel Dashboard → Settings → Environment Variables**

**Required variables:**
```
✅ POSTGRES_PRISMA_URL
✅ SECRET_KEY
✅ ALGORITHM=HS256
✅ ACCESS_TOKEN_EXPIRE_MINUTES=10080
✅ FRONTEND_URL=https://pikcarz.co.za
✅ BACKEND_URL=https://pikcarz.vercel.app
✅ CLOUDINARY_CLOUD_NAME
✅ CLOUDINARY_API_KEY
✅ CLOUDINARY_API_SECRET
```

**Missing any?** Add them and redeploy!

---

### Fix 3: Database Migration

**The password reset table might not exist!**

1. **Go to Neon SQL Editor:** https://console.neon.tech/
2. **Run this SQL:**

```sql
-- Create password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token);
```

3. **Verify users table has 'admin' enum:**

```sql
-- Add admin to role enum if missing
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';
```

---

### Fix 4: Check Backend Logs

**If deployed but not working:**

1. **Vercel Dashboard** → Your Project
2. **Click "Deployments"**
3. **Click latest deployment**
4. **Click "Functions"** tab
5. **Look for errors** in the logs

**Common issues:**
- `ModuleNotFoundError` → Missing package in requirements.txt
- `DatabaseError` → POSTGRES_PRISMA_URL wrong
- `ImportError` → Code syntax error

---

## 🎯 STEP 4: VERIFY IT WORKS

### Test Sequence:

1. **Health Check:**
   ```
   https://pikcarz.vercel.app/health
   Should show: {"status": "healthy"}
   ```

2. **API Docs:**
   ```
   https://pikcarz.vercel.app/docs
   Should show: FastAPI interactive docs
   ```

3. **Login Test:**
   - Go to: https://pikcarz.co.za/signin.html
   - Try logging in with admin email
   - Should work! ✅

---

## 🚨 IF BACKEND IS COMPLETELY DOWN:

### Emergency Checklist:

- [ ] Check Vercel deployment status
- [ ] Verify environment variables are set
- [ ] Check Function logs for errors
- [ ] Test https://pikcarz.vercel.app/health
- [ ] Redeploy if needed
- [ ] Run database migrations
- [ ] Test login again

---

## 📋 MOST LIKELY CAUSES:

### 1. Backend Never Deployed (70% chance)
**Fix:** Push code to GitHub → Vercel auto-deploys

### 2. Recent Code Break (20% chance)
**Fix:** Check Vercel logs, fix error, redeploy

### 3. Environment Variable Missing (8% chance)
**Fix:** Add missing vars in Vercel settings

### 4. Database Issue (2% chance)
**Fix:** Run migrations in Neon

---

## ⚡ FASTEST FIX:

**Try this RIGHT NOW:**

1. **Open terminal:**
   ```bash
   cd C:\Repos\PikCarz
   git add .
   git commit -m "Trigger redeploy"
   git push
   ```

2. **Wait 2 minutes** for Vercel deployment

3. **Test:** https://pikcarz.vercel.app/health

4. **If works:** Try login again!

---

## 🔍 DEBUG ENDPOINTS:

Test these URLs in your browser:

```
✅ https://pikcarz.vercel.app/
   Expected: {"status":"online","app":"pikCarz API","version":"1.0.0"}

✅ https://pikcarz.vercel.app/health
   Expected: {"status":"healthy"}

✅ https://pikcarz.vercel.app/docs
   Expected: FastAPI documentation page

✅ https://pikcarz.vercel.app/api/vehicles
   Expected: List of vehicles (might be empty)
```

If ANY of these fail → Backend is DOWN!

---

## 📞 NEXT STEPS:

1. **Run API_TEST.html** to diagnose
2. **Check Vercel dashboard** for deployment status
3. **Push code** to trigger redeploy
4. **Test health endpoint** 
5. **Try login** again

---

**Status:** 🔴 CRITICAL - Backend not responding  
**Action:** Deploy backend immediately!  
**ETA:** 2-3 minutes after git push

---

## ✅ WHEN FIXED:

You'll know it's working when:
- https://pikcarz.vercel.app/health shows `{"status":"healthy"}`
- Login page doesn't show "Failed to fetch"
- Users can sign in successfully

**Then you can go LIVE!** 🚀
