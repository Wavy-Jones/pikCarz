# 🚀 FINAL DEPLOYMENT CHECKLIST - pikcarz.co.za

**Domain:** pikcarz.co.za (GoDaddy)  
**Status:** Ready to Deploy  
**Target:** Monday Launch

---

## ✅ PART 1: PUSH CODE TO GITHUB (5 minutes)

### Step 1: Commit All Changes

```bash
cd C:\Repos\PikCarz
git status  # Review what changed
git add .
git commit -m "Complete platform: Custom domain, API integration, Cloudinary, subscriptions, PayFast"
git push
```

**What This Deploys:**
- ✅ CNAME file (pikcarz.co.za)
- ✅ Updated CORS settings
- ✅ Browse page with real API
- ✅ Admin dashboard
- ✅ Cloudinary image upload
- ✅ Subscription plans
- ✅ PayFast integration

**Deployment Time:** 2-3 minutes (GitHub Pages auto-deploys)

---

## ✅ PART 2: CONFIGURE GODADDY DNS (10 minutes)

### Step 1: Login to GoDaddy

1. Go to https://dcc.godaddy.com/domains
2. Find **pikcarz.co.za**
3. Click **"DNS"** or **"Manage DNS"**

### Step 2: Delete Existing Records

Delete these if they exist:
- Any A records pointing to parking pages
- Any CNAME for @ (root)

### Step 3: Add GitHub Pages Records

**Add 4 A Records:**

Click "Add" → Select "A"
1. Name: `@` | Value: `185.199.108.153` | TTL: 600
2. Name: `@` | Value: `185.199.109.153` | TTL: 600
3. Name: `@` | Value: `185.199.110.153` | TTL: 600
4. Name: `@` | Value: `185.199.111.153` | TTL: 600

**Add WWW CNAME:**

Click "Add" → Select "CNAME"
- Name: `www`
- Value: `wavy-jones.github.io`
- TTL: 1 hour

### Step 4: Save Changes

Click "Save" and wait for confirmation.

**DNS Propagation:** 15-60 minutes

---

## ✅ PART 3: CONFIGURE GITHUB PAGES (2 minutes)

1. Go to: `https://github.com/Wavy-Jones/pikCarz/settings/pages`
2. Under **"Custom domain"**, enter: `pikcarz.co.za`
3. Click **"Save"**
4. Wait 10-15 minutes
5. ✅ Check **"Enforce HTTPS"**

**SSL Certificate:** Takes 10-15 minutes to provision

---

## ✅ PART 4: SET UP CLOUDINARY (5 minutes)

### Step 1: Create Account

1. Go to: https://cloudinary.com
2. Sign up (FREE tier - 25 GB storage, 25 credits/month)
3. Verify email

### Step 2: Get Credentials

1. Go to Dashboard
2. Copy these values:
   - **Cloud Name:** (e.g., `dk123abc`)
   - **API Key:** (e.g., `123456789012345`)
   - **API Secret:** (e.g., `abcdef123456...`)

### Step 3: Add to Vercel

1. Go to Vercel Dashboard → Your project
2. Settings → Environment Variables
3. Add these:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

4. Click "Save"

---

## ✅ PART 5: SET UP PAYFAST (10 minutes)

### Step 1: Create Account

1. Go to: https://www.payfast.co.za
2. Sign up for merchant account
3. Verify email and business details

### Step 2: Get Credentials

1. Go to Settings → Integration
2. Copy:
   - **Merchant ID:** (10-digit number)
   - **Merchant Key:** (random string)
3. Set a **Passphrase** (create a secure one)

### Step 3: Add to Vercel

Go to Vercel → Settings → Environment Variables

Add these:

```
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
PAYFAST_PASSPHRASE=your_passphrase
PAYFAST_MODE=sandbox
```

**Important:** Use `sandbox` mode for testing!

### Step 4: Configure Webhooks

In PayFast dashboard:
1. Go to Settings → Integration
2. Add Notify URL: `https://pikcarz.vercel.app/api/subscriptions/webhook/payfast`
3. Save

---

## ✅ PART 6: UPDATE VERCEL ENVIRONMENT VARIABLES (5 minutes)

**Check ALL these are set in Vercel:**

### Required (Should Already Exist):
```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
POSTGRES_PRISMA_URL=postgresql://... (auto-created by Neon)
ADMIN_EMAIL=admin@pikcarz.co.za
ADMIN_PASSWORD=your_admin_password
```

### New (Add These):
```
FRONTEND_URL=https://pikcarz.co.za
BACKEND_URL=https://pikcarz.vercel.app
CLOUDINARY_CLOUD_NAME=your_value
CLOUDINARY_API_KEY=your_value
CLOUDINARY_API_SECRET=your_value
PAYFAST_MERCHANT_ID=your_value
PAYFAST_MERCHANT_KEY=your_value
PAYFAST_PASSPHRASE=your_value
PAYFAST_MODE=sandbox
```

---

## ✅ PART 7: REDEPLOY BACKEND (1 minute)

After adding environment variables:

1. Go to Vercel Dashboard → Deployments
2. Click "⋯" on latest deployment
3. Click **"Redeploy"**
4. Wait 2-3 minutes

This ensures new environment variables are loaded.

---

## ✅ PART 8: CREATE ADMIN USER (10 minutes)

### Option A: Via PowerShell

```powershell
# 1. Register admin user
$admin = @{
    email = "admin@pikcarz.co.za"
    password = "Admin2026!Secure"
    full_name = "Gershon Mbhalati"
    role = "individual"
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin -ContentType "application/json"

Write-Host "User ID: $($response.user.id)"
```

### Option B: Via Swagger

1. Go to: `https://pikcarz.vercel.app/docs`
2. Find `POST /api/auth/register`
3. Use this JSON:
```json
{
  "email": "admin@pikcarz.co.za",
  "password": "Admin2026!Secure",
  "full_name": "Gershon Mbhalati",
  "role": "individual"
}
```

### Step 2: Upgrade to Admin in Database

1. Go to Vercel → Storage → Neon Database
2. Click "SQL Editor" or "Query"
3. Run:

```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'admin@pikcarz.co.za';
```

4. Verify:

```sql
SELECT id, email, role 
FROM users 
WHERE email = 'admin@pikcarz.co.za';
```

Should show: `role: admin`

---

## ✅ PART 9: TESTING (15 minutes)

### Test 1: Domain Access (After DNS Propagation)

Wait 15-60 minutes after DNS setup, then:

```bash
# Check DNS
nslookup pikcarz.co.za
```

Should show GitHub IPs (185.199.108.153, etc.)

**Browser Tests:**
1. `https://pikcarz.co.za` → Should load homepage
2. `https://www.pikcarz.co.za` → Should redirect to pikcarz.co.za
3. Green padlock (HTTPS) → Should appear

### Test 2: API Connection

1. Go to: `https://pikcarz.co.za/browse.html`
2. Open browser console (F12)
3. Should see: "Loading vehicles..."
4. Should show: Empty state or any existing vehicles
5. **No CORS errors** in console

### Test 3: Admin Dashboard

1. Go to: `https://pikcarz.co.za/admin.html`
2. Login: `admin@pikcarz.co.za` / `Admin2026!Secure`
3. Should show admin dashboard
4. Stats should load (might be all zeros)

### Test 4: Create Test Vehicle

1. Register normal user at `/docs`
2. Create vehicle via `POST /api/vehicles`
3. Check admin dashboard → should appear in "Pending"
4. Approve vehicle
5. Check browse page → should appear there

### Test 5: Subscription Plans

1. Go to `/docs`
2. Execute: `GET /api/subscriptions/plans`
3. Should return 5 plans (Free, Standard, Premium, Dealer Basic, Dealer Pro)

### Test 6: Image Upload (Optional)

1. Create vehicle
2. Use `POST /api/vehicles/{id}/images` at `/docs`
3. Upload test image
4. Should return URL from Cloudinary

---

## 🚨 TROUBLESHOOTING

### DNS Not Working
**Issue:** `pikcarz.co.za` doesn't load  
**Solution:** Wait longer (up to 60 mins), clear DNS cache:
```bash
ipconfig /flushdns
```

### HTTPS Certificate Error
**Issue:** "Your connection is not private"  
**Solution:** Wait 10-15 minutes for GitHub to provision SSL

### CORS Error
**Issue:** Console shows CORS error  
**Solution:** 
1. Check Vercel FRONTEND_URL = `https://pikcarz.co.za`
2. Redeploy backend
3. Clear browser cache

### Admin Login Fails
**Issue:** "Access denied"  
**Solution:** Check role in database is `admin`, not `individual`

### Images Not Uploading
**Issue:** 500 error on image upload  
**Solution:** Check Cloudinary credentials in Vercel env vars

### PayFast Webhook Fails
**Issue:** Payments not activating subscription  
**Solution:** 
1. Check webhook URL in PayFast dashboard
2. Verify passphrase matches in Vercel
3. Check Vercel function logs

---

## 📊 DEPLOYMENT STATUS TRACKER

Mark each step as you complete it:

**Sunday Night:**
- [ ] Code pushed to GitHub
- [ ] GoDaddy DNS configured
- [ ] GitHub Pages custom domain set
- [ ] Cloudinary account created
- [ ] Cloudinary credentials added to Vercel
- [ ] PayFast account created
- [ ] PayFast credentials added to Vercel
- [ ] Backend redeployed with new env vars

**Wait 15-60 Minutes for DNS:**
- [ ] `pikcarz.co.za` resolves to GitHub IPs
- [ ] `www.pikcarz.co.za` redirects properly
- [ ] HTTPS certificate active (green padlock)

**Monday Morning:**
- [ ] Admin user created
- [ ] Admin role verified in database
- [ ] Admin login tested
- [ ] Test vehicle created
- [ ] Vehicle approval tested
- [ ] Browse page shows real data
- [ ] All systems operational

---

## 🎯 MONDAY DEMO CHECKLIST

Before showing Gershon:

- [ ] Domain loads: `pikcarz.co.za` ✓
- [ ] HTTPS working (green padlock) ✓
- [ ] Admin dashboard accessible ✓
- [ ] Can login as admin ✓
- [ ] At least 1 test vehicle exists ✓
- [ ] Can approve/reject vehicles ✓
- [ ] Stats update in real-time ✓
- [ ] Browse page shows vehicles ✓
- [ ] Subscription plans display ✓
- [ ] Payment flow tested (sandbox) ✓

---

## 🎉 FINAL SUCCESS CRITERIA

**You're ready for launch when:**

1. ✅ `https://pikcarz.co.za` loads the homepage
2. ✅ HTTPS is active (green padlock)
3. ✅ Admin can login at `/admin.html`
4. ✅ Admin can approve/reject vehicles
5. ✅ Browse page shows real vehicles from API
6. ✅ No CORS errors in console
7. ✅ Subscription plans are visible
8. ✅ Test payment completes (sandbox mode)

**When all checkboxes are ✓, YOU'RE LIVE! 🚀**

---

## 📞 SUPPORT

**Issues? Check:**
1. Vercel function logs (for backend errors)
2. Browser console (for frontend errors)
3. Neon database (for data issues)
4. DNS propagation checker: https://dnschecker.org

**Everything documented in:**
- `DOMAIN_SETUP_GUIDE.md` - DNS configuration
- `ADMIN_SETUP_GUIDE.md` - Admin user setup
- `MONDAY_READY.md` - Launch strategy

---

## 🚀 YOU'RE READY!

**Push the code now and start the deployment process!**

**Time to complete:** 60-90 minutes (including DNS propagation)  
**Result:** Professional vehicle marketplace live at `pikcarz.co.za` 🎉
