# 🚀 VERCEL ENVIRONMENT VARIABLES UPDATE GUIDE

## ⚠️ CRITICAL: YOU MUST UPDATE THESE IN VERCEL!

The code fix is only HALF the solution. Vercel uses environment variables that override the code defaults. **You MUST update these in the Vercel dashboard!**

---

## 📋 STEP-BY-STEP GUIDE

### Step 1: Open Vercel Dashboard
1. Go to: **https://vercel.com/dashboard**
2. Log in with your account
3. You should see your **pikCarz** project listed

### Step 2: Navigate to Environment Variables
1. **Click** on the **pikCarz** project card
2. **Click** the **Settings** tab (in the top menu)
3. **Click** **Environment Variables** (in the left sidebar)

### Step 3: Update FRONTEND_URL
1. **Find** the variable named: `FRONTEND_URL`
2. **Click** the **...** (three dots) next to it
3. **Click** **Edit**
4. **Change the value from:**
   ```
   https://wavy-jones.github.io/pikCarz
   ```
5. **Change to:**
   ```
   https://pikcarz.co.za
   ```
6. **Click** **Save**

### Step 4: Add PAYFAST_MODE Variable
1. **Click** **Add Environment Variable** button
2. **Name:** `PAYFAST_MODE`
3. **Value:** `live`
4. **Environment:** Select all environments (Production, Preview, Development)
5. **Click** **Save**

### Step 5: Trigger Redeploy
**IMPORTANT:** Changing environment variables doesn't automatically redeploy!

1. **Click** the **Deployments** tab (in the top menu)
2. **Find** the most recent deployment (top of the list)
3. **Click** the **...** (three dots) on the right
4. **Click** **Redeploy**
5. **Confirm** the redeploy
6. **Wait** 2-3 minutes for deployment to complete
7. **Look for** green checkmark ✅ = Success!

---

## ✅ VERIFICATION

### After Redeploy Completes:

**Test 1: Check API Health**
1. Open: https://pikcarz.vercel.app/health
2. Should show: `{"status":"healthy"}`

**Test 2: Check Browse Page**
1. Open: https://pikcarz.co.za/browse.html
2. Click: **Motorbikes** button
3. Should load vehicles (not "Failed to fetch")
4. Open browser console (F12)
5. Should see NO CORS errors

**Test 3: Check Environment Variables**
1. In Vercel dashboard
2. Go to: Settings → Environment Variables
3. Verify:
   - `FRONTEND_URL` = `https://pikcarz.co.za` ✅
   - `PAYFAST_MODE` = `live` ✅

---

## 🔍 TROUBLESHOOTING

### If Browse Page Still Shows "Failed to Fetch":

**Check 1: Did you redeploy?**
- Changing env variables doesn't auto-redeploy
- You MUST manually redeploy from Deployments tab

**Check 2: Is the deployment successful?**
- Look for green checkmark in Deployments
- If red X, click it to see error logs

**Check 3: Are the variables correct?**
- Go back to Settings → Environment Variables
- Double-check spelling and values
- Make sure no extra spaces

**Check 4: Clear browser cache**
- Press `Ctrl + Shift + R` for hard refresh
- Or press `Ctrl + F5`

### If PayFast Still in Sandbox:

**Check:** `PAYFAST_MODE` environment variable
- Must be exactly: `live` (lowercase)
- Not: `Live`, `LIVE`, `production`, etc.

---

## 📊 CURRENT VS. CORRECT VALUES

### BEFORE (Broken):
```
FRONTEND_URL = https://wavy-jones.github.io/pikCarz
PAYFAST_MODE = (not set, defaults to "sandbox")
```

### AFTER (Working):
```
FRONTEND_URL = https://pikcarz.co.za
PAYFAST_MODE = live
```

---

## ⚠️ IMPORTANT NOTES

### About Environment Variables in Vercel:
- They override values in code
- Changes don't take effect until redeploy
- Must be set for the correct environment (Production)
- Case-sensitive!

### About PayFast Live Mode:
- **REAL money** will be charged
- Make sure PayFast merchant account is **approved**
- Test with **small amounts** first
- Have **support contact** ready

---

## 🎯 QUICK CHECKLIST

- [ ] Logged into Vercel dashboard
- [ ] Opened pikCarz project
- [ ] Went to Settings → Environment Variables
- [ ] Updated `FRONTEND_URL` to `https://pikcarz.co.za`
- [ ] Added `PAYFAST_MODE` with value `live`
- [ ] Saved both variables
- [ ] Went to Deployments tab
- [ ] Clicked ... → Redeploy on latest deployment
- [ ] Waited for green checkmark
- [ ] Tested browse page - it works! ✅
- [ ] Checked console - no CORS errors! ✅

---

## 🚨 IF YOU SKIP THIS STEP

**The browse page will STILL be broken!**

Even though the code is updated, Vercel uses the environment variables you set in the dashboard. If you don't update them, it will keep using the old wrong values.

**YOU MUST UPDATE VERCEL VARIABLES!**

---

## 🎉 AFTER THIS IS DONE

**Everything will work:**
- ✅ Browse page loads vehicles
- ✅ All category filters work
- ✅ No CORS errors
- ✅ PayFast in live mode
- ✅ Ready for real users!

---

## 📞 SUMMARY

**What to do:**
1. Update `FRONTEND_URL` in Vercel to `https://pikcarz.co.za`
2. Add `PAYFAST_MODE` with value `live`
3. Redeploy from Deployments tab
4. Wait 2-3 minutes
5. Test browse page

**Time needed:** 5 minutes

**Difficulty:** Easy (just clicking buttons in dashboard)

**Result:** Browse page works perfectly! ✅

---

**GO UPDATE VERCEL NOW!** 🚀
