"""
Database connection and session management
Configured for Vercel serverless + Neon PostgreSQL.

NullPool is required for serverless: each request gets a fresh connection
that is immediately released when the request ends. Persistent pool_size/
max_overflow settings cause connection exhaustion on Neon when multiple
Vercel cold-start invocations run simultaneously.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.config import settings

# NullPool: no persistent pool — each DB operation opens and closes its own
# connection. Essential for serverless environments (Vercel + Neon).
_db_url = settings.db_url

if _db_url:
    engine = create_engine(_db_url, poolclass=NullPool)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

# Base class for models
Base = declarative_base()

# Dependency for routes
def get_db():
    if SessionLocal is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Database is not configured. Set DATABASE_URL or POSTGRES_PRISMA_URL environment variable."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
