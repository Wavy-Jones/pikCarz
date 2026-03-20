# 🚨 EMERGENCY GO-LIVE PROCEDURE
## Get pikCarz Live in 10 Minutes!

---

## ⚡ STEP 1: DEPLOY BACKEND (2 minutes)

### Open Terminal:

```bash
cd C:\Repos\PikCarz

# Add all files
git add .

# Commit with message
git commit -m "Emergency deployment - fix login and go live"

# Push to GitHub (triggers Vercel deployment)
git push
```

### Wait for Deployment:
- **Go to:** https://vercel.com/dashboard
- **Watch:** Deployment progress (1-2 minutes)
- **Wait for:** Green checkmark ✅

---

## 🔍 STEP 2: TEST BACKEND (1 minute)

### Test 1: Health Check
**Open in browser:** https://pikcarz.vercel.app/health

**Expected Response:**
```json
{"status":"healthy"}
```

**If you see this:** ✅ Backend is LIVE!  
**If error/timeout:** ❌ Check Vercel logs, something failed

### Test 2: API Docs
**Open in browser:** https://pikcarz.vercel.app/docs

**Expected:** FastAPI documentation page loads  
**If loads:** ✅ API is working!

---

## 💾 STEP 3: DATABASE SETUP (3 minutes)

### Go to Neon:
1. **Visit:** https://console.neon.tech/
2. **Select:** pikcarz-db
3. **Click:** SQL Editor

### Run Setup SQL:

**Copy this entire block and run:**

```sql
-- Add admin role to enum
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin';

-- Create password reset table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_password_reset_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_user ON password_reset_tokens(user_id);

-- Verify setup
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM vehicles) as vehicles,
    (SELECT COUNT(*) FROM users WHERE role = 'admin') as admins;
```

**Expected:** Query runs successfully, shows counts  
**If runs:** ✅ Database is configured!

---

## 👨‍💼 STEP 4: CREATE ADMIN ACCOUNTS (2 minutes)

### Method 1: Via DevTools (Easiest)

1. **Open any webpage** (even Google)
2. **Press F12** → Console tab
3. **Paste this code:**

```javascript
async function createAdmin(name, email, password) {
  const response = await fetch('https://pikcarz.vercel.app/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name: name, role: "individual" })
  });
  const data = await response.json();
  console.log(response.ok ? `✅ ${name} created!` : `❌ ${data.detail}`);
}

await createAdmin('Gershon Mbhalati', 'gershon@pikcarz.co.za', 'Gershon2026!Secure');
await createAdmin('Davy-Jones Mhangwana', 'davy@pikcarz.co.za', 'DavyJones2026!Secure');
await createAdmin('Admin Support', 'admin3@pikcarz.co.za', 'Admin32026!Secure');
```

**If accounts already exist, you'll see "Email already registered" - that's OK!**

### Upgrade to Admin:

**Back in Neon SQL Editor, run:**

```sql
UPDATE users 
SET role = 'admin' 
WHERE email IN (
  'gershon@pikcarz.co.za',
  'davy@pikcarz.co.za',
  'admin3@pikcarz.co.za'
);

-- Verify
SELECT email, full_name, role FROM users WHERE role = 'admin';
```

**Expected:** Shows all 3 admins with role='admin'  
**If shows:** ✅ Admin accounts ready!

---

## 🧪 STEP 5: TEST LOGIN (1 minute)

### Test Admin Login:

1. **Go to:** https://pikcarz.co.za/signin.html
2. **Enter:**
   - Email: gershon@pikcarz.co.za
   - Password: Gershon2026!Secure
3. **Click:** Sign In

**Expected:** Redirects to admin-dashboard.html  
**If redirects:** ✅ LOGIN WORKS!

---

## ✅ STEP 6: FINAL VERIFICATION (1 minute)

### Quick Test Suite:

1. **Homepage:** https://pikcarz.co.za/ → Loads? ✅
2. **Browse:** https://pikcarz.co.za/browse.html → Loads? ✅
3. **Sign In:** Works? ✅
4. **Admin Dashboard:** Accessible? ✅

**ALL YES?** 🎉 **YOU'RE LIVE!**

---

## 🚀 YOU'RE LIVE! WHAT NOW?

### Immediate Tasks:

1. ✅ Platform is accessible
2. ✅ Users can register
3. ✅ Admins can login
4. ✅ Basic functionality works

### Next Steps (can do later):

- [ ] Set up Cloudinary (for image uploads)
- [ ] Set up SendGrid (for emails)
- [ ] Set up PayFast (for payments)
- [ ] Test full vehicle approval workflow
- [ ] Monitor Vercel logs for errors

---

## 🆘 IF SOMETHING DOESN'T WORK:

### "Failed to fetch" Still Shows:

**Check Vercel:**
1. Go to Vercel Dashboard
2. Click "Deployments"
3. Latest deployment should be green ✅
4. If red ❌ → Click it → View logs → See error

**Common fixes:**
- Wait 2-3 minutes for deployment
- Clear browser cache (Ctrl+Shift+R)
- Check https://pikcarz.vercel.app/health in new tab

### Can't Login:

**Check:**
1. Backend health: https://pikcarz.vercel.app/health
2. Admin accounts created in database
3. Role upgraded to 'admin' in SQL
4. Correct password being used

### Database Errors:

**Run in Neon:**
```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Should show: users, vehicles, payments, password_reset_tokens
```

---

## 📊 MONITORING (First 24 Hours)

**Check these every few hours:**

1. **Vercel Function Logs:**
   - Vercel Dashboard → Deployments → Latest → Functions
   - Look for errors

2. **User Registrations:**
   - Neon SQL: `SELECT COUNT(*) FROM users;`
   - Should increase as people register

3. **Vehicle Listings:**
   - Neon SQL: `SELECT COUNT(*) FROM vehicles;`
   - Should increase as people list vehicles

---

## 🎯 SUCCESS METRICS:

**After going live, track:**

- ✅ Users can visit pikcarz.co.za
- ✅ Users can register
- ✅ Users can login
- ✅ Users can browse vehicles
- ✅ Users can create listings
- ✅ Admins can approve listings
- ✅ No errors in Vercel logs

---

## 📞 EMERGENCY HOTLINE:

**If platform goes down:**

1. **Check Vercel status:** https://www.vercel-status.com/
2. **Check Neon status:** https://neon.tech/status
3. **Redeploy:** `git push` to trigger new deployment
4. **Rollback:** In Vercel, promote previous working deployment

---

## ⏱️ TOTAL TIME: ~10 MINUTES

1. Deploy backend: 2 min
2. Test backend: 1 min
3. Database setup: 3 min
4. Create admins: 2 min
5. Test login: 1 min
6. Final checks: 1 min

---

## 🎉 CONGRATULATIONS!

**Once all steps pass, your platform is LIVE and ready for users!**

**Status:** 🟢 LIVE  
**URL:** https://pikcarz.co.za  
**Admin:** https://pikcarz.co.za/signin.html

---

**Now go get those customers! 🚀**
