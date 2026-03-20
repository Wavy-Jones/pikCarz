# 🚀 PRE-LAUNCH CHECKLIST - pikCarz Platform

## ✅ COMPLETE TESTING CHECKLIST

**Test EVERY item before going live!**

---

## 1. 🔌 BACKEND API TESTS

### 1.1 Health Check
- [ ] Visit: https://pikcarz.vercel.app/health
- [ ] Expected: `{"status":"healthy"}`
- [ ] Status: __________

### 1.2 API Documentation
- [ ] Visit: https://pikcarz.vercel.app/docs
- [ ] Expected: FastAPI interactive docs page
- [ ] Can see all endpoints listed
- [ ] Status: __________

### 1.3 Root Endpoint
- [ ] Visit: https://pikcarz.vercel.app/
- [ ] Expected: JSON with app name and version
- [ ] Status: __________

---

## 2. 🔐 AUTHENTICATION TESTS

### 2.1 User Registration
- [ ] Go to: https://pikcarz.co.za/signin.html → "Create one"
- [ ] Fill in test user details
- [ ] Click "Create Account"
- [ ] Expected: Redirects to dashboard
- [ ] Status: __________

### 2.2 Admin Login
- [ ] Go to: https://pikcarz.co.za/signin.html
- [ ] Login with: gershon@pikcarz.co.za (or your admin email)
- [ ] Expected: Redirects to admin-dashboard.html
- [ ] Status: __________

### 2.3 Regular User Login
- [ ] Go to: https://pikcarz.co.za/signin.html
- [ ] Login with test user
- [ ] Expected: Redirects to dashboard.html
- [ ] Status: __________

### 2.4 Logout
- [ ] Click logout button in dashboard
- [ ] Expected: Returns to homepage
- [ ] Token cleared from localStorage
- [ ] Status: __________

### 2.5 Password Reset Flow
- [ ] Go to: https://pikcarz.co.za/forgot-password.html
- [ ] Enter your email
- [ ] Check email inbox (or Vercel logs)
- [ ] Click reset link
- [ ] Set new password
- [ ] Try logging in with new password
- [ ] Status: __________

---

## 3. 🚗 VEHICLE LISTING TESTS

### 3.1 Browse Vehicles
- [ ] Go to: https://pikcarz.co.za/browse.html
- [ ] Expected: Shows vehicle listings
- [ ] Status: __________

### 3.2 Create Vehicle Listing (User Dashboard)
- [ ] Login as regular user
- [ ] Go to dashboard
- [ ] Click "List Vehicle" or similar
- [ ] Fill in vehicle details
- [ ] Upload images
- [ ] Submit
- [ ] Expected: Vehicle created, shows in "My Listings"
- [ ] Status: __________

### 3.3 Vehicle Approval (Admin Dashboard)
- [ ] Login as admin
- [ ] Go to admin dashboard
- [ ] See pending vehicle in list
- [ ] Click "Approve"
- [ ] Expected: Vehicle moves to approved
- [ ] Status: __________

### 3.4 Vehicle Appears on Browse Page
- [ ] After approval, go to browse.html
- [ ] Expected: Approved vehicle shows up
- [ ] Status: __________

### 3.5 Vehicle Detail Page
- [ ] Click on a vehicle from browse page
- [ ] Expected: Shows full vehicle details
- [ ] Images display correctly
- [ ] Contact seller button works
- [ ] Status: __________

---

## 4. 🖼️ IMAGE UPLOAD TESTS

### 4.1 Cloudinary Configuration
- [ ] Vercel env vars contain CLOUDINARY_* variables
- [ ] Status: __________

### 4.2 Upload Vehicle Images
- [ ] Create vehicle listing
- [ ] Upload 2-3 images
- [ ] Expected: Images upload successfully
- [ ] Images display in listing
- [ ] Status: __________

### 4.3 Delete Vehicle Images
- [ ] Edit vehicle listing
- [ ] Delete an image
- [ ] Expected: Image removed
- [ ] Status: __________

---

## 5. 👨‍💼 ADMIN DASHBOARD TESTS

### 5.1 Dashboard Access
- [ ] Login as admin
- [ ] Redirects to admin-dashboard.html
- [ ] Dashboard loads without errors
- [ ] Status: __________

### 5.2 Platform Statistics
- [ ] See total users count
- [ ] See total vehicles count
- [ ] See pending approvals count
- [ ] Status: __________

### 5.3 Pending Vehicles List
- [ ] See list of pending vehicles
- [ ] Each vehicle shows details
- [ ] Status: __________

### 5.4 Approve Vehicle
- [ ] Click "Approve" on pending vehicle
- [ ] Expected: Vehicle approved, removed from pending
- [ ] Status: __________

### 5.5 Reject Vehicle
- [ ] Click "Reject" on pending vehicle
- [ ] Expected: Vehicle rejected
- [ ] Status: __________

### 5.6 Multiple Admin Accounts
- [ ] Test all 3 admin accounts can login
- [ ] All have access to admin dashboard
- [ ] Status: __________

---

## 6. 👤 USER DASHBOARD TESTS

### 6.1 Dashboard Access
- [ ] Login as regular user
- [ ] Redirects to dashboard.html
- [ ] Dashboard loads
- [ ] Status: __________

### 6.2 My Listings
- [ ] See user's vehicle listings
- [ ] Shows status (pending/active/rejected)
- [ ] Status: __________

### 6.3 Edit Listing
- [ ] Click edit on own listing
- [ ] Update details
- [ ] Save changes
- [ ] Expected: Changes saved
- [ ] Status: __________

### 6.4 Delete Listing
- [ ] Click delete on own listing
- [ ] Confirm deletion
- [ ] Expected: Listing removed
- [ ] Status: __________

### 6.5 Subscription Status
- [ ] See current subscription tier
- [ ] See listings remaining
- [ ] Status: __________

---

## 7. 💳 PAYMENT/SUBSCRIPTION TESTS

### 7.1 PayFast Configuration
- [ ] Vercel env vars contain PAYFAST_* variables
- [ ] Status: __________

### 7.2 View Subscription Plans
- [ ] Go to subscriptions/pricing page
- [ ] See all plans listed
- [ ] Status: __________

### 7.3 Subscribe to Plan (Sandbox Mode)
- [ ] Click subscribe on a plan
- [ ] Redirects to PayFast
- [ ] Status: __________

---

## 8. 📧 EMAIL TESTS

### 8.1 SendGrid Configuration
- [ ] Vercel env vars contain SENDGRID_API_KEY
- [ ] SendGrid sender verified
- [ ] Status: __________

### 8.2 Password Reset Email
- [ ] Request password reset
- [ ] Receive email
- [ ] Email looks professional
- [ ] Reset link works
- [ ] Status: __________

### 8.3 Welcome Email
- [ ] Register new user
- [ ] Receive welcome email
- [ ] Email looks good
- [ ] Status: __________

---

## 9. 🎨 FRONTEND TESTS

### 9.1 Homepage
- [ ] Go to: https://pikcarz.co.za/
- [ ] All sections load
- [ ] Stats display correctly
- [ ] CTA buttons work
- [ ] Logo displays
- [ ] Status: __________

### 9.2 Browse Page
- [ ] Go to: https://pikcarz.co.za/browse.html
- [ ] Vehicles load
- [ ] Filters work
- [ ] Search works
- [ ] Status: __________

### 9.3 About Page
- [ ] Go to: https://pikcarz.co.za/about.html
- [ ] Content displays
- [ ] Status: __________

### 9.4 Contact Page
- [ ] Go to: https://pikcarz.co.za/contact.html
- [ ] Form works
- [ ] Status: __________

### 9.5 Mobile Responsiveness
- [ ] Test on mobile device or resize browser
- [ ] All pages responsive
- [ ] Navigation works
- [ ] Status: __________

---

## 10. 🔒 SECURITY TESTS

### 10.1 Protected Routes
- [ ] Try accessing dashboard.html without login
- [ ] Expected: Redirects to signin
- [ ] Status: __________

### 10.2 Admin-Only Routes
- [ ] Login as regular user
- [ ] Try accessing admin-dashboard.html
- [ ] Expected: Redirected or blocked
- [ ] Status: __________

### 10.3 Password Security
- [ ] Passwords are hashed (not visible in database)
- [ ] JWT tokens expire correctly
- [ ] Status: __________

---

## 11. 🌐 DEPLOYMENT TESTS

### 11.1 DNS Configuration
- [ ] pikcarz.co.za loads correctly
- [ ] www.pikcarz.co.za redirects (if configured)
- [ ] HTTPS active
- [ ] Status: __________

### 11.2 Backend Deployment
- [ ] Vercel deployment successful
- [ ] All functions running
- [ ] No errors in logs
- [ ] Status: __________

### 11.3 Database Connection
- [ ] Backend can connect to Neon database
- [ ] All tables exist
- [ ] Status: __________

---

## 12. 🐛 ERROR HANDLING TESTS

### 12.1 Invalid Login
- [ ] Try login with wrong password
- [ ] Expected: Error message displayed
- [ ] Status: __________

### 12.2 Network Error Handling
- [ ] Disable network, try action
- [ ] Expected: Error message shown
- [ ] Status: __________

### 12.3  404 Pages
- [ ] Visit non-existent page
- [ ] Expected: Friendly error message
- [ ] Status: __________

---

## 13. 📊 PERFORMANCE TESTS

### 13.1 Page Load Speed
- [ ] Homepage loads in < 3 seconds
- [ ] Browse page loads in < 3 seconds
- [ ] Dashboard loads in < 3 seconds
- [ ] Status: __________

### 13.2 API Response Time
- [ ] API calls respond in < 1 second
- [ ] Status: __________

---

## 14. 🔧 FINAL CHECKS

### 14.1 Environment Variables
- [ ] All required vars set in Vercel
- [ ] No test/dummy values in production
- [ ] Status: __________

### 14.2 Database Migrations
- [ ] All tables created
- [ ] password_reset_tokens table exists
- [ ] userrole enum includes 'admin'
- [ ] Status: __________

### 14.3 Admin Accounts
- [ ] All 3 admin accounts created
- [ ] All upgraded to admin role
- [ ] All can login
- [ ] Status: __________

### 14.4 Remove Mock Data
- [ ] Remove hardcoded vehicle cards from index.html
- [ ] Remove mock data from browse.html
- [ ] Status: __________

### 14.5 Production Settings
- [ ] PAYFAST_MODE=sandbox or live?
- [ ] Debug mode OFF
- [ ] Status: __________

---

## ✅ GO-LIVE CRITERIA

**ALL items above must be checked before going live!**

### Critical Items (Must Work):
- ✅ Backend health check passes
- ✅ User can register
- ✅ User can login
- ✅ Admin can login
- ✅ Vehicles display on browse page
- ✅ Admin can approve vehicles
- ✅ Images upload successfully

### Nice-to-Have (Can fix post-launch):
- ⚠️ Email sending (can use console logs temporarily)
- ⚠️ PayFast subscriptions (can enable later)
- ⚠️ Perfect mobile responsiveness

---

## 🚨 EMERGENCY CONTACTS

**If something breaks after launch:**

1. Check Vercel logs: https://vercel.com/dashboard
2. Check Neon database: https://console.neon.tech/
3. Check SendGrid: https://app.sendgrid.com/
4. Check Cloudinary: https://cloudinary.com/console

---

## 📝 POST-LAUNCH MONITORING

**Monitor these daily for first week:**

- [ ] Vercel function execution logs
- [ ] Database query performance
- [ ] Email delivery rates
- [ ] User registration count
- [ ] Vehicle approval times
- [ ] Error rates in logs

---

**Last Updated:** March 22, 2026  
**Status:** 🔴 Pre-Launch Testing In Progress  
**Go-Live Target:** ASAP after all checks pass!
