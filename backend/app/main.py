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

# ── Import routers ────────────────────────────────────────────────────────────
from app.api import auth, vehicles, admin, subscriptions
from app.api import favourites, search_alerts

# ── Initialize app first (before DB ops, so startup errors return JSON) ───────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://pikcarz.co.za",
        "https://www.pikcarz.co.za",
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "*",
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


# ── DB table creation + migration: run once at startup via lifespan ───────────
# Using @app.on_event rather than module-level code so errors are caught and
# returned as JSON rather than killing the process silently.
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

        # Safe migration: add contact columns if they don't already exist
        with engine.connect() as conn:
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_name VARCHAR;"
            ))
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_phone VARCHAR;"
            ))
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS views INTEGER NOT NULL DEFAULT 0;"
            ))
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS whatsapp_leads INTEGER NOT NULL DEFAULT 0;"
            ))
            conn.execute(text(
                "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS email_leads INTEGER NOT NULL DEFAULT 0;"
            ))
            conn.commit()
    except Exception as e:
        # Log but don't crash — tables likely already exist
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
