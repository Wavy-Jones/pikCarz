# pikCarz Backend API

FastAPI backend for the pikCarz vehicle marketplace platform.

## 🚀 Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Auth:** JWT tokens (python-jose)
- **Image Storage:** Cloudinary
- **Payments:** PayFast
- **Hosting:** Railway.app

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py          # User model
│   │   ├── vehicle.py       # Vehicle model
│   │   └── payment.py       # Payment model
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   └── subscription.py
│   ├── api/                 # API routes
│   │   ├── auth.py          # Authentication
│   │   ├── vehicles.py      # Vehicle CRUD (to be added)
│   │   ├── subscriptions.py # Subscription management (to be added)
│   │   ├── admin.py         # Admin panel (to be added)
│   │   └── payments.py      # PayFast webhook (to be added)
│   ├── core/                # Core utilities
│   │   ├── security.py      # JWT & password hashing
│   │   └── deps.py          # FastAPI dependencies
│   └── services/            # External services
│       ├── cloudinary.py    # Image upload (to be added)
│       └── payfast.py       # Payment processing (to be added)
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── Procfile                 # Railway deployment
└── railway.json             # Railway configuration
```

---

## ⚡ Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` and fill in:
- `DATABASE_URL` - Your PostgreSQL connection string
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `CLOUDINARY_*` - Get from cloudinary.com
- `PAYFAST_*` - Get from payfast.co.za

### 3. Run the Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --port 8000

# Or use Python directly
python -m app.main
```

API will be available at: **http://localhost:8000**

Swagger docs: **http://localhost:8000/docs**

---

## 🗄️ Database Setup

### Option 1: Local PostgreSQL

```bash
# Install PostgreSQL
# Create database
createdb pikcarz

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/pikcarz
```

### Option 2: Railway PostgreSQL (Recommended)

1. Go to [railway.app](https://railway.app)
2. Create new project → Add PostgreSQL
3. Copy `DATABASE_URL` from Railway
4. Paste into `.env`

Tables will be created automatically on first run.

---

## 🚀 Deployment (Railway)

### Quick Deploy

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### Environment Variables on Railway

Set these in Railway dashboard:
- `DATABASE_URL` (auto-provided by Railway Postgres)
- `SECRET_KEY`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `PAYFAST_MERCHANT_ID`
- `PAYFAST_MERCHANT_KEY`
- `PAYFAST_PASSPHRASE`
- `FRONTEND_URL=https://wavy-jones.github.io/pikCarz`

---

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Vehicles (To be added)
- `GET /api/vehicles` - List all vehicles
- `POST /api/vehicles` - Create listing
- `GET /api/vehicles/{id}` - Get vehicle details
- `PUT /api/vehicles/{id}` - Update vehicle
- `DELETE /api/vehicles/{id}` - Delete vehicle

### Subscriptions (To be added)
- `GET /api/subscriptions/plans` - List plans
- `POST /api/subscriptions/subscribe` - Subscribe

### Payments (To be added)
- `POST /api/payments/webhook` - PayFast webhook

### Admin (To be added)
- `GET /api/admin/vehicles/pending` - Pending listings
- `PUT /api/admin/vehicles/{id}/approve` - Approve
- `PUT /api/admin/vehicles/{id}/reject` - Reject

---

## 🛠️ Next Steps (Complete by Monday)

1. ✅ Basic setup (done)
2. ⏳ Add vehicle CRUD endpoints
3. ⏳ Add image upload (Cloudinary)
4. ⏳ Add subscription management
5. ⏳ Add PayFast integration
6. ⏳ Add admin routes
7. ⏳ Deploy to Railway
8. ⏳ Connect frontend

---

## 🔐 Security

- Passwords hashed with bcrypt
- JWT tokens expire in 7 days
- CORS configured for frontend only
- SQL injection protection via SQLAlchemy
- Rate limiting (to be added)

---

## 📊 Database Models

### User
- Individual sellers & vehicle dealers
- Subscription tiers
- Dealer verification status

### Vehicle
- All listing details
- Images (Cloudinary URLs)
- Status (pending, active, sold, expired)

### Payment
- PayFast transaction records
- Subscription tracking
- Webhook data storage

---

## 🐛 Debugging

```bash
# Check logs
railway logs

# Test API locally
curl http://localhost:8000/

# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","full_name":"Test User"}'
```

---

**Status:** MVP in progress - targeting Monday launch 🚀
