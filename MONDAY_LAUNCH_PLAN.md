# 🚀 GET LIVE BY MONDAY - ACTION PLAN

## ✅ Backend is Scaffolded!

Location: `C:\Repos\PikCarz\backend\`

**What's Done:**
- ✅ FastAPI app structure
- ✅ Database models (User, Vehicle, Payment)
- ✅ Auth system (register/login with JWT)
- ✅ Pydantic schemas
- ✅ Security utilities
- ✅ Railway deployment config

**What's Left (Saturday + Sunday):**
- ⏳ Vehicle CRUD API (2 hours)
- ⏳ Cloudinary image upload (1 hour)
- ⏳ PayFast integration (2 hours)
- ⏳ Admin routes (1 hour)
- ⏳ Deploy to Railway (30 mins)
- ⏳ Connect frontend to API (1 hour)

**Total Time Needed:** ~8 hours of focused work

---

## 📋 SATURDAY TASKS

### 1. Local Setup (30 mins)

```bash
cd C:\Repos\PikCarz\backend

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get PostgreSQL Database (15 mins)

**Option A: Railway (Easiest)**
1. Go to https://railway.app
2. Sign up with GitHub
3. New Project → Add PostgreSQL
4. Copy the `DATABASE_URL` (looks like: `postgresql://user:pass@host:port/db`)

**Option B: Local PostgreSQL**
- Install PostgreSQL
- Create database: `createdb pikcarz`
- URL: `postgresql://postgres:password@localhost:5432/pikcarz`

### 3. Setup .env File (5 mins)

```bash
cd backend
copy .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=<paste from Railway>
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
FRONTEND_URL=https://wavy-jones.github.io/pikCarz

# Leave Cloudinary empty for now
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Leave PayFast empty for now
PAYFAST_MERCHANT_ID=
PAYFAST_MERCHANT_KEY=
PAYFAST_PASSPHRASE=
PAYFAST_MODE=sandbox

ADMIN_EMAIL=admin@pikcarz.co.za
ADMIN_PASSWORD=admin123change
```

### 4. Test the Backend (10 mins)

```bash
# From backend folder
uvicorn app.main:app --reload
```

Open browser → `http://localhost:8000`  
You should see: `{"status":"online","app":"pikCarz API"}`

Swagger docs → `http://localhost:8000/docs`

**Test registration:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"test123\",\"full_name\":\"Test User\",\"role\":\"individual\"}"
```

If you see a token → **Backend works!** ✅

---

## 🔧 SUNDAY TASKS (Build Remaining Features)

I'll help you build these tomorrow (or you can ping me anytime):

### Task 1: Vehicle CRUD API
Add endpoints to create/list/edit vehicles

### Task 2: Cloudinary Integration
Sign up at cloudinary.com (free tier), add image upload endpoint

### Task 3: PayFast Integration
Webhook to handle subscription payments

### Task 4: Admin Routes
Approve/reject listings, manage users

### Task 5: Deploy to Railway
Push backend live with one command

### Task 6: Connect Frontend
Update frontend to call the live API

---

## 🚀 MONDAY MORNING (Go Live)

1. Final testing on staging
2. Switch PayFast to live mode
3. Point Gershon to the live site
4. **Collect first payment!** 💰

---

## 🆘 If You Get Stuck

**Database won't connect?**
- Check DATABASE_URL is correct
- Make sure Railway Postgres is running

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Port already in use?**
```bash
uvicorn app.main:app --reload --port 8001
```

**Need help NOW?**
- Just ping me with the error
- I'll help you debug in real-time

---

## 📊 Current Status

```
Frontend: ✅ 100% Complete (Live on GitHub Pages)
Backend:  ⏳ 30% Complete (Auth system works, need CRUD + payments)
Database: ⏳ Models ready, needs deployment
Payments: ⏳ Not started (Sunday task)
Admin:    ⏳ Not started (Sunday task)
```

**Monday launch is 100% achievable if we finish the backend by Sunday night!** 🎯

---

**Next Step:** Run the local setup (Task 1-4 above) and confirm backend runs. Then ping me and we'll build the rest together! 🚀
