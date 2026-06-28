"""
pikCarz Backend API — FastAPI entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings

# ── Import models (required before create_all) ────────────────────────────────
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.payment import Payment
from app.models.favourite import Favourite
from app.models.search_alert import SearchAlert
from app.models.page_view import PageView

# ── Import routers ────────────────────────────────────────────────────────────
from app.api import auth, vehicles, admin, subscriptions
from app.api import favourites, search_alerts
from app.api import analytics, referrals, contact

# ── Initialize app first (before DB ops, so startup errors return JSON) ───────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# NOTE: do NOT include "*" here — it conflicts with allow_credentials=True
# and causes browsers to block requests even when the origin is correct.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://pikcarz.co.za",
        "https://www.pikcarz.co.za",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Catch-all exception handler: always returns JSON, never a bare 500 ────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__},
    )

# ── Include routers ───────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(admin.router)
app.include_router(subscriptions.router)
app.include_router(favourites.router)
app.include_router(search_alerts.router)
app.include_router(analytics.router)
app.include_router(referrals.router)
app.include_router(contact.router)


# ── DB table creation + migration: run once at startup via lifespan ───────────
@app.on_event("startup")
async def startup_db():
    try:
        from app.database import Base, engine
        from sqlalchemy import text

        if engine is None:
            print("[startup] No database URL configured — skipping table creation.")
            return

        # Create any missing tables (idempotent)
        Base.metadata.create_all(bind=engine)

        # Safe migrations: add columns if they don't already exist
        migrations = [
            # vehicles
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_name VARCHAR;",
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_phone VARCHAR;",
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS views INTEGER NOT NULL DEFAULT 0;",
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS whatsapp_leads INTEGER NOT NULL DEFAULT 0;",
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS email_leads INTEGER NOT NULL DEFAULT 0;",
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS report_url TEXT;",
            # users
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS dealer_address TEXT;",
            # referral system
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_code VARCHAR(16);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by INTEGER REFERENCES users(id) ON DELETE SET NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_count INTEGER NOT NULL DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_founding_dealer BOOLEAN NOT NULL DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_ambassador BOOLEAN NOT NULL DEFAULT FALSE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS priority_search_until TIMESTAMPTZ;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS featured_listing_until TIMESTAMPTZ;",
            # backfill referral codes for existing users
            "UPDATE users SET referral_code = UPPER(SUBSTRING(MD5(id::text || 'pikcarz') FOR 8)) WHERE referral_code IS NULL;",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_referral_code ON users(referral_code) WHERE referral_code IS NOT NULL;",
            """CREATE TABLE IF NOT EXISTS referrals (
                id          SERIAL PRIMARY KEY,
                referrer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                referred_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );""",
            "CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);",
            # recurring billing (PayFast subscription token)
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS payfast_token VARCHAR;",
            "CREATE INDEX IF NOT EXISTS idx_users_payfast_token ON users (payfast_token);",
            # sold vehicles — "Mark as Sold" feature
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS sold_at TIMESTAMPTZ;",
            """CREATE TABLE IF NOT EXISTS sold_vehicles (
                id         SERIAL PRIMARY KEY,
                vehicle_id INTEGER NOT NULL,
                owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
                make       VARCHAR NOT NULL,
                model      VARCHAR NOT NULL,
                year       INTEGER,
                price      NUMERIC(12,2),
                sold_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );""",
            "CREATE INDEX IF NOT EXISTS idx_sold_vehicles_sold_at ON sold_vehicles(sold_at);",
        ]

        with engine.connect() as conn:
            for sql in migrations:
                try:
                    conn.execute(text(sql))
                except Exception as col_err:
                    print(f"[startup] Migration skipped ({col_err}): {sql}")
            conn.commit()

    except Exception as e:
        print(f"[startup] DB migration note: {e}")


# ── Health / root ──────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"status": "online", "app": settings.APP_NAME, "version": settings.VERSION}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
