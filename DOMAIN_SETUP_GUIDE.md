# 🌐 DOMAIN SETUP: pikcarz.co.za (GoDaddy)

## ✅ COMPLETE CONFIGURATION GUIDE

**Your Domain:** `pikcarz.co.za`  
**Registrar:** GoDaddy  
**Frontend:** GitHub Pages  
**Backend:** Vercel (pikcarz.vercel.app)

---

## 📋 STEP 1: Configure DNS in GoDaddy (5 minutes)

### Login to GoDaddy DNS Management

1. Go to https://dcc.godaddy.com/domains
2. Find `pikcarz.co.za`
3. Click **"DNS"** or **"Manage DNS"**

---

### Add These DNS Records:

**For Frontend (GitHub Pages):**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 185.199.108.153 | 600 |
| A | @ | 185.199.109.153 | 600 |
| A | @ | 185.199.110.153 | 600 |
| A | @ | 185.199.111.153 | 600 |
| CNAME | www | wavy-jones.github.io | 1 hour |

**For Backend (Vercel) - Optional Subdomain:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | api | cname.vercel-dns.com | 1 hour |

---

### Detailed GoDaddy Instructions:

1. **Remove Existing A Records:**
   - Delete any existing A records pointing to parking pages
   - Delete any CNAME for @ if it exists

2. **Add GitHub Pages A Records:**
   - Click **"Add Record"**
   - Type: **A**
   - Name: **@** (this means root domain)
   - Value: **185.199.108.153**
   - TTL: **600**
   - Click **"Save"**
   - Repeat for all 4 IP addresses (108, 109, 110, 111)

3. **Add WWW CNAME:**
   - Click **"Add Record"**
   - Type: **CNAME**
   - Name: **www**
   - Value: **wavy-jones.github.io** (no dot at the end)
   - TTL: **1 hour**
   - Click **"Save"**

4. **Optional - Add API Subdomain:**
   - Click **"Add Record"**
   - Type: **CNAME**
   - Name: **api**
   - Value: **cname.vercel-dns.com**
   - TTL: **1 hour**
   - Click **"Save"**

---

## 📋 STEP 2: Configure GitHub Pages (2 minutes)

### Add Custom Domain to GitHub

1. Go to your GitHub repo: `https://github.com/Wavy-Jones/pikCarz`
2. Click **"Settings"** (top menu)
3. Scroll to **"Pages"** (left sidebar)
4. Under **"Custom domain"**, enter: `pikcarz.co.za`
5. Click **"Save"**
6. ✅ Check **"Enforce HTTPS"** (wait 5-10 minutes for certificate)

**GitHub will create a CNAME file in your repo - don't delete it!**

---

## 📋 STEP 3: Create CNAME File in Repository

GitHub Pages needs a CNAME file in your repo root.

**Create this file manually if GitHub didn't create it:**

File: `C:\Repos\PikCarz\CNAME`
Content: `pikcarz.co.za`

Then push:
```bash
cd C:\Repos\PikCarz
git add CNAME
git commit -m "Add custom domain CNAME"
git push
```

---

## 📋 STEP 4: Update Backend CORS Settings

Update Vercel environment variables:

1. Go to **Vercel Dashboard** → Your project
2. Click **"Settings"** → **"Environment Variables"**
3. Find `FRONTEND_URL`
4. Change from: `https://wavy-jones.github.io/pikCarz`
5. Change to: `https://pikcarz.co.za`
6. Click **"Save"**
7. **Redeploy** the backend (Vercel → Deployments → Redeploy)

**Add these variables if using API subdomain:**
```
BACKEND_URL=https://api.pikcarz.co.za
```

---

## 📋 STEP 5: Update Frontend API URLs

Update the API base URL in your JavaScript:

**File:** `C:\Repos\PikCarz\js\api.js`

**Change:**
```javascript
const API_CONFIG = {
  BASE_URL: 'https://pikcarz.vercel.app',  // Old
  TIMEOUT: 10000
};
```

**To:**
```javascript
const API_CONFIG = {
  BASE_URL: 'https://pikcarz.vercel.app',  // Keep this OR use 'https://api.pikcarz.co.za' if you set up subdomain
  TIMEOUT: 10000
};
```

**Recommendation:** Keep using `pikcarz.vercel.app` for backend since it's already set up and working. The API subdomain is optional.

---

## 📋 STEP 6: Update Admin Dashboard

**File:** `C:\Repos\PikCarz\admin.html`

Find:
```javascript
const API_BASE = 'https://pikcarz.vercel.app';
```

Keep this as-is (no change needed).

---

## 🧪 TESTING & VERIFICATION

### Test DNS Propagation (15-60 minutes after setup)

**Check DNS:**
```bash
nslookup pikcarz.co.za
```

**Should show:**
```
Non-authoritative answer:
Name:    pikcarz.co.za
Addresses:  185.199.108.153
            185.199.109.153
            185.199.110.153
            185.199.111.153
```

**Check WWW:**
```bash
nslookup www.pikcarz.co.za
```

**Should show:**
```
www.pikcarz.co.za
    canonical name = wavy-jones.github.io
```

---

### Test Website Access

1. **Wait 15-60 minutes** for DNS propagation
2. Go to `http://pikcarz.co.za` (should redirect to HTTPS)
3. Go to `https://pikcarz.co.za` (should load your site)
4. Go to `https://www.pikcarz.co.za` (should redirect to non-www)

**If HTTPS shows error:** Wait 10-15 minutes for GitHub to provision SSL certificate.

---

### Test API Access

1. Go to `https://pikcarz.co.za/browse.html`
2. Open browser console (F12)
3. Should see vehicles loading from API
4. No CORS errors

---

## 🚨 TROUBLESHOOTING

### "DNS_PROBE_FINISHED_NXDOMAIN" Error
- **Cause:** DNS not propagated yet
- **Fix:** Wait 15-60 minutes, clear DNS cache:
  ```bash
  ipconfig /flushdns  # Windows
  ```

### "Your connection is not private" (HTTPS Error)
- **Cause:** SSL certificate not ready
- **Fix:** Wait 10-15 minutes, GitHub is provisioning certificate

### CORS Error in Browser Console
- **Cause:** Backend CORS not updated
- **Fix:** Update FRONTEND_URL in Vercel environment variables

### Site loads but shows GitHub 404
- **Cause:** CNAME file missing or incorrect
- **Fix:** Create CNAME file with `pikcarz.co.za` content

### www subdomain not working
- **Cause:** CNAME record incorrect
- **Fix:** Verify CNAME points to `wavy-jones.github.io` (no trailing dot)

---

## 📊 EXPECTED TIMELINE

| Step | Time |
|------|------|
| DNS Configuration | 5 minutes |
| GitHub Pages Setup | 2 minutes |
| DNS Propagation | 15-60 minutes |
| SSL Certificate | 10-15 minutes |
| **Total Time** | **30-80 minutes** |

---

## ✅ VERIFICATION CHECKLIST

After setup:

- [ ] DNS A records point to GitHub Pages IPs
- [ ] CNAME record for www points to wavy-jones.github.io
- [ ] GitHub Pages custom domain set to pikcarz.co.za
- [ ] CNAME file exists in repository
- [ ] HTTPS enforced in GitHub Pages settings
- [ ] Vercel FRONTEND_URL updated to pikcarz.co.za
- [ ] Backend redeployed with new CORS settings
- [ ] http://pikcarz.co.za loads (redirects to HTTPS)
- [ ] https://pikcarz.co.za loads with green padlock
- [ ] https://www.pikcarz.co.za redirects to pikcarz.co.za
- [ ] Browse page loads vehicles from API
- [ ] No CORS errors in console
- [ ] Admin dashboard works at pikcarz.co.za/admin.html

---

## 🎉 WHAT YOU'LL HAVE AFTER SETUP

**Frontend URLs:**
- Homepage: `https://pikcarz.co.za`
- Browse: `https://pikcarz.co.za/browse.html`
- Admin: `https://pikcarz.co.za/admin.html`
- About: `https://pikcarz.co.za/about.html`
- Contact: `https://pikcarz.co.za/contact.html`

**Backend URLs:**
- API: `https://pikcarz.vercel.app`
- API Docs: `https://pikcarz.vercel.app/docs`

**Optional API Subdomain:**
- API: `https://api.pikcarz.co.za` (if you set up CNAME)

---

## 📝 NOTES

1. **DNS Propagation:** Can take 15 minutes to 48 hours (usually 15-60 minutes)
2. **SSL Certificate:** GitHub provides free HTTPS via Let's Encrypt
3. **WWW Redirect:** GitHub automatically redirects www to non-www
4. **API Domain:** You can keep using pikcarz.vercel.app for API (it's free and works perfectly)
5. **Email:** If you want email (info@pikcarz.co.za), you'll need to set up MX records separately

---

## 🚀 NEXT STEPS AFTER DNS SETUP

1. **Push updated code** (with CNAME file)
2. **Wait for DNS propagation** (15-60 mins)
3. **Test all URLs** work correctly
4. **Update all marketing materials** to use pikcarz.co.za
5. **Create admin user** for Monday demo
6. **Final testing** before launch!

---

**Your professional domain is ready to go! 🎉**
