# 📧 SENDGRID QUICK START (5 MINUTE VERSION)

## 🚀 SUPER FAST SETUP

### 1. Create Account (2 min)
→ https://signup.sendgrid.com/
→ Use work email
→ Choose FREE plan (100 emails/day)
→ Verify email

### 2. Get API Key (1 min)
→ Login: https://app.sendgrid.com/
→ Settings → API Keys
→ Create API Key → Full Access
→ **COPY KEY NOW!** (Only shown once)

### 3. Verify Sender (1 min)
→ Settings → Sender Authentication
→ Verify a Single Sender
→ From: noreply@pikcarz.co.za
→ Check email → Click verify link

### 4. Add to Vercel (1 min)
→ Vercel Dashboard → pikCarz → Settings → Environment Variables

**Add these 2 variables:**
```
SENDGRID_API_KEY = SG.your-key-here
EMAIL_FROM = noreply@pikcarz.co.za
```

### 5. Deploy (30 sec)
```bash
git add .
git commit -m "Add SendGrid"
git push
```

## ✅ TEST IT

1. Go to: https://pikcarz.co.za/forgot-password.html
2. Enter your email
3. Check inbox → Should receive reset email! 📧

---

## 🔑 IMPORTANT LINKS

- **Sign Up:** https://signup.sendgrid.com/
- **Dashboard:** https://app.sendgrid.com/
- **Full Guide:** See `SENDGRID_SETUP_COMPLETE.md`

---

## 💡 QUICK TIPS

- ✅ Free = 100 emails/day (enough for now!)
- ✅ Always verify sender email first
- ✅ Check spam folder if emails don't arrive
- ✅ Monitor in: Dashboard → Activity

---

**Total Time: ~5 minutes!** ⚡
