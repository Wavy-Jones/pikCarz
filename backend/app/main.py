"""
pikCarz Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine

# Import models to create tables
from app.models.user import User
from app.models.vehicle import Vehicle  
from app.models.payment import Payment

# Import routers
from app.api import auth, vehicles, admin, subscriptions

# Create database tables
Base.metadata.create_all(bind=engine)

# Safe migration: add contact columns if they don't already exist
# (create_all won't add columns to existing tables)
try:
    with engine.connect() as conn:
        from sqlalchemy import text
        conn.execute(text(
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_name VARCHAR;"
        ))
        conn.execute(text(
            "ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS contact_phone VARCHAR;"
        ))
        conn.commit()
except Exception as e:
    print(f"Migration note: {e}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://pikcarz.co.za",
        "https://www.pikcarz.co.za",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(admin.router)
app.include_router(subscriptions.router)

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }

@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
