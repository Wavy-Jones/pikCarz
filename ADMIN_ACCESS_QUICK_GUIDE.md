# 🔐 ADMIN DASHBOARD - QUICK ACCESS GUIDE

## 🎯 Step-by-Step Admin Setup (10 Minutes)

### Step 1: Register Admin User (2 minutes)

**Option A: Using PowerShell (Easiest)**

```powershell
# Run this in PowerShell
$admin = @{
    email = "admin@pikcarz.co.za"
    password = "YourSecurePassword123!"
    full_name = "Gershon Mbhalati"
    role = "individual"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin -ContentType "application/json"
```

**Save the user ID from the response!**

---

**Option B: Using Browser (Swagger UI)**

1. Go to: https://pikcarz.vercel.app/docs
2. Find `POST /api/auth/register`
3. Click "Try it out"
4. Paste this JSON:

```json
{
  "email": "admin@pikcarz.co.za",
  "password": "YourSecurePassword123!",
  "full_name": "Gershon Mbhalati",
  "role": "individual"
}
```

5. Click "Execute"
6. **Save the user ID!**

---

### Step 2: Upgrade to Admin in Database (5 minutes)

1. **Go to Vercel Dashboard:**
   - https://vercel.com/dashboard
   - Click on your project

2. **Go to Storage:**
   - Click "Storage" tab
   - Click on your Neon database
   - Click "SQL Editor" or "Query"

3. **Run this SQL:**

```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'admin@pikcarz.co.za';
```

4. **Verify it worked:**

```sql
SELECT id, email, full_name, role 
FROM users 
WHERE email = 'admin@pikcarz.co.za';
```

Should show: `role: admin` ✓

---

### Step 3: Login to Admin Dashboard (1 minute)

1. **Go to:** https://pikcarz.co.za/admin.html

2. **Login with:**
   - Email: `admin@pikcarz.co.za`
   - Password: `YourSecurePassword123!`

3. **You'll see:**
   - Platform stats dashboard
   - Pending vehicles list
   - Approve/Reject buttons

---

## 🧪 Test the Dashboard (5 minutes)

### Create a Test Vehicle:

**Via Swagger UI:**
1. Go to: https://pikcarz.vercel.app/docs
2. Login first (use /api/auth/login)
3. Find `POST /api/vehicles`
4. Create a test vehicle:

```json
{
  "make": "Toyota",
  "model": "Corolla",
  "year": 2023,
  "category": "used_car",
  "price": 250000,
  "mileage": 15000,
  "transmission": "Automatic",
  "fuel_type": "Petrol",
  "color": "White",
  "title": "2023 Toyota Corolla - Excellent Condition",
  "description": "Well maintained, full service history",
  "province": "Gauteng",
  "city": "Johannesburg"
}
```

### Then Test Admin Approval:

1. Refresh admin dashboard
2. You should see the Toyota Corolla in pending list
3. Click "✓ Approve"
4. Vehicle disappears from pending
5. Stats update automatically

✅ **Success!** Admin dashboard is working!

---

## 📱 Admin Dashboard Features

### Platform Overview Stats:
- Total Users
- Total Vehicles
- Active Listings
- Pending Approval
- Verified Dealers

### Pending Vehicles:
- List of all vehicles awaiting approval
- Vehicle details (make, model, price, seller)
- Quick approve/reject buttons
- Auto-refresh after action

### Actions:
- ✓ **Approve:** Makes vehicle visible on browse page
- ✗ **Reject:** Removes vehicle from system
- 🔄 **Refresh:** Reload dashboard data

---

## 🚨 Troubleshooting

### "Access denied. Admin privileges required"
**Fix:** User role is not 'admin' in database. Re-run Step 2.

### "Invalid credentials"
**Fix:** Check email/password spelling.

### "Failed to load stats"
**Fix:** Backend might be down. Check pikcarz.vercel.app/docs

### No pending vehicles showing
**Fix:** Create a test vehicle first! Empty list is expected if no vehicles exist.

---

## 🎯 For Monday Demo

### Quick Demo Script:

1. **Show homepage:** "This is pikcarz.co.za - live on our custom domain"

2. **Create vehicle:** Use Swagger to create a test listing → "Notice it's pending approval"

3. **Login as admin:** Go to admin.html → "Here's the control panel"

4. **Approve vehicle:** Click approve button → "Watch it go live"

5. **Show stats:** "Platform automatically tracks everything"

**Result:** Gershon sees the complete workflow in action! ✓

---

## 🔑 Admin Credentials

**URL:** https://pikcarz.co.za/admin.html

**Email:** admin@pikcarz.co.za  
**Password:** [Set your own secure password]

**Security:**
- JWT token expires after 7 days
- Token stored in browser localStorage
- Logout button clears session

---

## ✅ ADMIN SETUP CHECKLIST

Before Monday:
- [ ] Admin user registered
- [ ] Role upgraded to 'admin' in database
- [ ] Admin login tested successfully
- [ ] Can see dashboard stats (might be zeros)
- [ ] Created 1 test vehicle
- [ ] Successfully approved test vehicle
- [ ] Tested reject function
- [ ] Dashboard refresh button works

**Status:** ✅ Ready when checklist complete!

---

## 🎉 YOU'RE DONE!

Admin dashboard is fully functional and ready for Monday's demo!
