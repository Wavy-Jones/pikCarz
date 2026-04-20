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
engine = create_engine(
    settings.db_url,
    poolclass=NullPool,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
