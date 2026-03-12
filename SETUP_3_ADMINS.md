# 👥 SETUP 3 ADMIN ACCOUNTS - COMPLETE GUIDE

## 🎯 Quick Summary

This guide will help you create 3 admin accounts that can all access the admin dashboard at `pikcarz.co.za/admin-dashboard.html` by signing in at `pikcarz.co.za/signin.html`.

---

## 📋 Admin Accounts to Create

| Name | Email | Role |
|------|-------|------|
| Gershon Mbhalati | gershon@pikcarz.co.za | Admin |
| Davy-Jones Mhangwana | davy@pikcarz.co.za | Admin |
| Admin 3 | admin3@pikcarz.co.za | Admin |

---

## 🚀 METHOD 1: Using PowerShell (Easiest - 5 Minutes)

### Step 1: Register All 3 Users

**Copy and run this in PowerShell:**

```powershell
# Admin 1: Gershon Mbhalati
$admin1 = @{
    email = "gershon@pikcarz.co.za"
    password = "Gershon2026!Secure"
    full_name = "Gershon Mbhalati"
    role = "individual"
} | ConvertTo-Json

$response1 = Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin1 -ContentType "application/json"
Write-Host "✅ Gershon registered - ID: $($response1.user.id)"

# Admin 2: Davy-Jones Mhangwana
$admin2 = @{
    email = "davy@pikcarz.co.za"
    password = "DavyJones2026!Secure"
    full_name = "Davy-Jones Mhangwana"
    role = "individual"
} | ConvertTo-Json

$response2 = Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin2 -ContentType "application/json"
Write-Host "✅ Davy-Jones registered - ID: $($response2.user.id)"

# Admin 3: General Admin
$admin3 = @{
    email = "admin3@pikcarz.co.za"
    password = "Admin32026!Secure"
    full_name = "Admin Support"
    role = "individual"
} | ConvertTo-Json

$response3 = Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin3 -ContentType "application/json"
Write-Host "✅ Admin3 registered - ID: $($response3.user.id)"

Write-Host "`n🎉 All 3 admins registered! Now run the SQL command to upgrade them."
```

---

### Step 2: Upgrade All 3 to Admin Role

**In Neon Database SQL Editor:**

1. Go to Vercel Dashboard → Storage → Your Database → SQL Editor
2. Run this SQL:

```sql
-- Upgrade all 3 users to admin role
UPDATE users 
SET role = 'admin' 
WHERE email IN (
  'gershon@pikcarz.co.za',
  'davy@pikcarz.co.za',
  'admin3@pikcarz.co.za'
);

-- Verify they're all admins
SELECT id, email, full_name, role 
FROM users 
WHERE email IN (
  'gershon@pikcarz.co.za',
  'davy@pikcarz.co.za',
  'admin3@pikcarz.co.za'
);
```

**Expected Output:**
```
3 rows updated
```

And you should see all 3 users with `role: admin`

---

## 🌐 METHOD 2: Using Swagger UI (Alternative)

### Step 1: Register Each Admin

1. Go to: `https://pikcarz.vercel.app/docs`
2. Find `POST /api/auth/register`
3. Click "Try it out"
4. Register each admin one by one:

**Admin 1 - Gershon:**
```json
{
  "email": "gershon@pikcarz.co.za",
  "password": "Gershon2026!Secure",
  "full_name": "Gershon Mbhalati",
  "role": "individual"
}
```

**Admin 2 - Davy-Jones:**
```json
{
  "email": "davy@pikcarz.co.za",
  "password": "DavyJones2026!Secure",
  "full_name": "Davy-Jones Mhangwana",
  "role": "individual"
}
```

**Admin 3:**
```json
{
  "email": "admin3@pikcarz.co.za",
  "password": "Admin32026!Secure",
  "full_name": "Admin Support",
  "role": "individual"
}
```

### Step 2: Same SQL as Method 1

Run the same SQL command from Method 1, Step 2.

---

## ✅ TEST THE ADMIN ACCOUNTS

### Test Each Admin Login:

1. **Go to:** `https://pikcarz.co.za/signin.html`

2. **Test Admin 1 (Gershon):**
   - Email: `gershon@pikcarz.co.za`
   - Password: `Gershon2026!Secure`
   - Should redirect to: `admin-dashboard.html` ✓

3. **Test Admin 2 (Davy-Jones):**
   - Email: `davy@pikcarz.co.za`
   - Password: `DavyJones2026!Secure`
   - Should redirect to: `admin-dashboard.html` ✓

4. **Test Admin 3:**
   - Email: `admin3@pikcarz.co.za`
   - Password: `Admin32026!Secure`
   - Should redirect to: `admin-dashboard.html` ✓

---

## 🔐 ADMIN CREDENTIALS SUMMARY

**Sign In URL:** `https://pikcarz.co.za/signin.html`

### Admin 1 - Gershon Mbhalati
- **Email:** gershon@pikcarz.co.za
- **Password:** Gershon2026!Secure
- **Access:** Full admin dashboard

### Admin 2 - Davy-Jones Mhangwana
- **Email:** davy@pikcarz.co.za
- **Password:** DavyJones2026!Secure
- **Access:** Full admin dashboard

### Admin 3 - General Admin
- **Email:** admin3@pikcarz.co.za
- **Password:** Admin32026!Secure
- **Access:** Full admin dashboard

---

## 🎯 HOW IT WORKS

### 1. Unified Sign-In System ✓
- All users (regular + admins) sign in at: `signin.html`
- No separate admin login page needed

### 2. Automatic Role-Based Redirect ✓
```javascript
if (user.role === 'admin') {
  redirect to → admin-dashboard.html
} else {
  redirect to → dashboard.html
}
```

### 3. Protected Admin Dashboard ✓
- `admin-dashboard.html` checks role on load
- Non-admins get redirected to signin
- Token-based authentication (JWT)

---

## 🧪 WORKFLOW DEMO

### Example Flow:

1. **Gershon visits:** `pikcarz.co.za`
2. **Clicks:** "Sign In" button
3. **Redirects to:** `pikcarz.co.za/signin.html`
4. **Enters credentials:**
   - Email: gershon@pikcarz.co.za
   - Password: Gershon2026!Secure
5. **System checks role:** `role = 'admin'`
6. **Auto-redirects to:** `admin-dashboard.html` ✅
7. **Shows admin dashboard** with:
   - Platform stats
   - Pending vehicles
   - Approve/Reject buttons

### Same Process for All 3 Admins!

---

## 🚨 TROUBLESHOOTING

### "Access denied - Admin privileges required"
**Problem:** User role is not set to 'admin' in database  
**Fix:** Re-run the SQL UPDATE command

### "Invalid credentials"
**Problem:** Wrong email or password  
**Fix:** Check spelling, passwords are case-sensitive

### Redirects to regular dashboard instead of admin
**Problem:** Role is not 'admin'  
**Fix:** Run this SQL:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your-email@pikcarz.co.za';
```

### Can't access admin-dashboard.html directly
**Problem:** This is correct behavior! You must sign in first  
**Fix:** Go to signin.html first, then login

---

## 📝 CHANGE PASSWORDS (Optional)

If you want to change passwords later, use this SQL:

```sql
-- Note: Passwords must be hashed with Argon2
-- Easiest way: Use the /api/auth/register endpoint to create
-- a new user with desired password, then copy the hash

-- Or update directly (requires generating Argon2 hash first)
UPDATE users 
SET hashed_password = 'argon2-hash-here' 
WHERE email = 'gershon@pikcarz.co.za';
```

**Recommendation:** Use the API to change passwords for proper hashing.

---

## ✅ SETUP CHECKLIST

Before Monday Demo:

- [ ] All 3 admin users registered via API
- [ ] All 3 upgraded to admin role in database
- [ ] Tested Gershon login → sees admin dashboard
- [ ] Tested Davy-Jones login → sees admin dashboard
- [ ] Tested Admin3 login → sees admin dashboard
- [ ] All "Sign In" buttons on website point to signin.html
- [ ] Regular users still go to dashboard.html
- [ ] Admin dashboard shows platform stats
- [ ] Created at least 1 test vehicle to approve

---

## 🎉 YOU'RE DONE!

**Status:** ✅ Multi-admin system ready!

All 3 admins can now:
- Sign in at the main website
- Get automatically redirected to admin dashboard
- View platform statistics
- Approve/reject vehicle listings
- Manage the platform

**Just like AuraBook!** 🚀

---

## 🔗 QUICK REFERENCE URLS

- **Homepage:** https://pikcarz.co.za
- **Sign In:** https://pikcarz.co.za/signin.html
- **Admin Dashboard:** https://pikcarz.co.za/admin-dashboard.html (auto-redirect after login)
- **User Dashboard:** https://pikcarz.co.za/dashboard.html (for regular users)
- **API Docs:** https://pikcarz.vercel.app/docs

---

**System Status:** ✅ Production Ready!
