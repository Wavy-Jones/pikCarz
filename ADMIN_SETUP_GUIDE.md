# 🔐 ADMIN SETUP GUIDE - CRITICAL FOR MONDAY

## ✅ Admin Dashboard Created!

**Location:** `https://wavy-jones.github.io/pikCarz/admin.html`

---

## 🚀 STEP 1: Create Admin User Account

### Option A: Via API (Recommended - 2 minutes)

**Open PowerShell and run:**

```powershell
# 1. Register admin user
$admin = @{
    email = "admin@pikcarz.co.za"
    password = "Admin2026!Secure"
    full_name = "Gershon Mbhalati"
    role = "individual"
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "https://pikcarz.vercel.app/api/auth/register" -Body $admin -ContentType "application/json"

Write-Host "Admin user created! ID: $($response.user.id)"
Write-Host "Token: $($response.access_token)"
```

**IMPORTANT:** Save the user ID - you'll need it for step 2!

---

### Option B: Via Swagger UI

1. Go to `https://pikcarz.vercel.app/docs`
2. Find `POST /api/auth/register`
3. Click "Try it out"
4. Use this JSON:
```json
{
  "email": "admin@pikcarz.co.za",
  "password": "Admin2026!Secure",
  "full_name": "Gershon Mbhalati",
  "role": "individual"
}
```
5. Click "Execute"
6. **Save the user ID from the response!**

---

## 🔧 STEP 2: Upgrade User to Admin (Database Update)

**You need to manually update the database to make this user an admin.**

### Using Neon Console:

1. Go to **Vercel Dashboard** → **Storage** → Your Neon database
2. Click **"SQL Editor"** or **"Query"**
3. Run this SQL command:

```sql
UPDATE users 
SET role = 'admin' 
WHERE email = 'admin@pikcarz.co.za';
```

4. Verify it worked:
```sql
SELECT id, email, full_name, role 
FROM users 
WHERE email = 'admin@pikcarz.co.za';
```

You should see `role: admin` in the result!

---

## 🎯 STEP 3: Test Admin Login

1. Go to `https://wavy-jones.github.io/pikCarz/admin.html`
2. Login with:
   - **Email:** `admin@pikcarz.co.za`
   - **Password:** `Admin2026!Secure`
3. You should see the admin dashboard!

---

## 📊 WHAT YOU'LL SEE IN THE DASHBOARD

### Platform Stats:
- Total Users
- Total Vehicles
- Active Listings
- Pending Approval
- Verified Dealers

### Pending Vehicles Section:
- List of all vehicles awaiting approval
- Approve button (✓) - Makes vehicle active
- Reject button (✗) - Rejects the listing
- Auto-refreshes after each action

---

## 🧪 TESTING THE ADMIN WORKFLOW

### Test Scenario:

1. **Create a test vehicle** (as regular user):
   - Register user: `test@pikcarz.co.za` / `test123456`
   - Create vehicle listing via API or Swagger
   - Vehicle will be status: "pending"

2. **Login as admin**:
   - Go to `admin.html`
   - Login with admin credentials
   - You should see the test vehicle in pending list

3. **Approve the vehicle**:
   - Click "✓ Approve" button
   - Vehicle disappears from pending list
   - Stats update automatically

4. **Verify on frontend**:
   - Vehicle should now appear in browse listings (when we connect API)

---

## 🔑 ADMIN CREDENTIALS (Share with Gershon)

**Admin Login URL:** `https://wavy-jones.github.io/pikCarz/admin.html`

**Email:** `admin@pikcarz.co.za`  
**Password:** `Admin2026!Secure`

*(Change password after first login if desired)*

---

## ⚠️ CRITICAL SECURITY NOTE

The admin dashboard uses JWT authentication. The token is stored in localStorage and expires after 7 days (10,080 minutes as configured).

**Important:**
- Keep admin credentials secure
- Only share with authorized personnel
- Change password regularly
- Consider 2FA in future versions

---

## 🚨 TROUBLESHOOTING

### "Access denied. Admin privileges required"
→ User role is not 'admin' in database. Re-run Step 2.

### "Invalid credentials"
→ Check email/password. Ensure user was created in Step 1.

### "Failed to load pending vehicles"
→ Check that backend is deployed and accessible at pikcarz.vercel.app

### Pending vehicles not showing
→ Create a test vehicle first! No vehicles = empty list.

---

## ✅ MONDAY MORNING CHECKLIST

Before showing Gershon:

- [ ] Admin user created in database
- [ ] Role updated to 'admin'
- [ ] Admin login tested successfully
- [ ] Can see dashboard stats
- [ ] Created at least 1 test vehicle
- [ ] Successfully approved test vehicle
- [ ] Test vehicle visible on browse page (when API connected)

---

## 🎉 YOU'RE READY FOR MONDAY!

The admin dashboard is now complete and functional. Gershon can:
- ✅ Login securely
- ✅ View platform statistics
- ✅ See all pending vehicles
- ✅ Approve vehicles with one click
- ✅ Reject vehicles with confirmation
- ✅ Refresh dashboard to see updates

**Next step:** Connect frontend browse.html to show real vehicles from API!
