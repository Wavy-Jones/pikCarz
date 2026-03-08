# 🚀 Deploy to Vercel WITHOUT CLI (via GitHub)

## Why This Method?

- ✅ No Vercel CLI installation needed
- ✅ No Node.js needed
- ✅ Deploy in 3 minutes
- ✅ Auto-deploys on every git push
- ✅ Same as how you deployed AuraBook!

---

## 📋 Step-by-Step (5 Minutes)

### 1. Push Backend to GitHub (1 min)

```bash
cd C:\Repos\PikCarz
git add .
git commit -m "Add FastAPI backend"
git push
```

**Verify:** Check GitHub → your repo should show a `backend` folder

---

### 2. Deploy on Vercel Dashboard (2 mins)

1. **Go to:** [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Click:** "Add New" → "Project"

3. **Import:** Select your GitHub repo `wavy-jones/pikcarz`

4. **Configure Project:**
   - **Framework Preset:** Other
   - **Root Directory:** `backend` ← IMPORTANT! Click "Edit" and type `backend`
   - **Build Command:** (leave empty)
   - **Output Directory:** (leave empty)
   - **Install Command:** `pip install -r requirements.txt`

5. **Click:** "Deploy"

Wait ~2 minutes. Vercel will give you a URL like:
```
https://pikcarz-backend.vercel.app
```

---

### 3. Add Environment Variables (2 mins)

**After deployment:**

1. Go to Project Settings → Environment Variables

2. Add these one by one:

```env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
FRONTEND_URL=https://wavy-jones.github.io/pikCarz
CLOUDINARY_CLOUD_NAME=your-cloudinary-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
PAYFAST_MERCHANT_ID=your-merchant-id
PAYFAST_MERCHANT_KEY=your-key
PAYFAST_PASSPHRASE=your-passphrase
PAYFAST_MODE=sandbox
ADMIN_EMAIL=admin@pikcarz.co.za
ADMIN_PASSWORD=changeme123
APP_NAME=pikCarz API
DEBUG=False
```

3. **Save** each variable

4. **Redeploy:**
   - Go to Deployments tab
   - Click 3 dots on latest deployment → "Redeploy"

---

### 4. Get Your Database (3 mins)

**Option A: Vercel Postgres** (Easiest)

1. In your Vercel project dashboard
2. Click "Storage" tab
3. Click "Create Database" → "Postgres"
4. Name it: `pikcarz-db`
5. Click "Create"
6. Copy the `POSTGRES_PRISMA_URL` value
7. Go to Environment Variables → Update `DATABASE_URL` with this value
8. Redeploy again

**Option B: Neon.tech** (Free alternative)

1. Go to [neon.tech](https://neon.tech)
2. Sign up → Create Project
3. Name: `pikcarz`
4. Copy connection string
5. Update `DATABASE_URL` on Vercel
6. Redeploy

---

### 5. Test It Works ✅

```bash
# Test health endpoint
curl https://your-project.vercel.app/

# Should return:
# {"status":"online","app":"pikCarz API","version":"1.0.0"}
```

**Or open in browser:**
```
https://your-project.vercel.app/docs
```

You should see the Swagger API documentation!

---

## 🔄 Auto-Deploy Setup

Once deployed via GitHub, every time you push code:

```bash
git add .
git commit -m "update backend"
git push
```

Vercel automatically redeploys! 🎉

---

## 🐛 Troubleshooting

### "Build failed"
- Check Root Directory is set to `backend`
- Check requirements.txt exists
- Look at build logs on Vercel dashboard

### "Module not found"
- Verify all imports use `from app.` not just `app.`
- Check vercel.json is in backend folder

### "Database connection error"
- Make sure DATABASE_URL includes `?sslmode=require`
- Verify Postgres is running (Vercel Storage tab)

### "502 Bad Gateway"
- Check Environment Variables are set
- Redeploy after adding env vars
- Look at Function Logs (Vercel dashboard)

---

## 📊 What You'll Get

After deployment:

✅ **Live API:** `https://pikcarz-backend.vercel.app`  
✅ **API Docs:** `https://pikcarz-backend.vercel.app/docs`  
✅ **Auto HTTPS:** Included  
✅ **Auto-deploy:** On every git push  
✅ **Free tier:** Plenty for MVP  

---

## 🎯 Next Steps After Deployment

1. ✅ Backend deployed
2. ⏳ Test registration: `POST /api/auth/register`
3. ⏳ Build remaining endpoints (vehicles, payments)
4. ⏳ Connect frontend to live API
5. ⏳ Go live Monday! 🚀

---

**No CLI needed! Deploy through the dashboard just like you did with AuraBook!** 🎉
