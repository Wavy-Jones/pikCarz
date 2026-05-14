"""
pikCarz Backend Configuration
"""
import os
import re
from pydantic_settings import BaseSettings
from typing import Optional


def _clean_db_url(url: str) -> str:
    """
    Strip parameters that are Prisma-specific and incompatible with SQLAlchemy.
    Vercel's POSTGRES_PRISMA_URL includes ?pgbouncer=true&connect_timeout=15
    which SQLAlchemy passes to libpq as unknown parameters, causing connection
    failures or silent query errors.
    """
    if not url:
        return url
    # Remove pgbouncer=true (Prisma connection-pooler flag)
    url = re.sub(r'[?&]pgbouncer=true', '', url)
    # Remove connect_timeout if present (already handled by SQLAlchemy)
    url = re.sub(r'[?&]connect_timeout=\d+', '', url)
    # Fix trailing ? or & left after stripping
    url = re.sub(r'\?$', '', url)
    url = re.sub(r'&$', '', url)
    return url


class Settings(BaseSettings):
    # App
    APP_NAME: str = "pikCarz API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Database
    # Vercel Postgres creates several URL env vars. Priority order for SQLAlchemy:
    #   1. DATABASE_URL          – custom env var set by us (most explicit)
    #   2. POSTGRES_URL_NON_POOLING – Vercel direct connection (no PgBouncer)
    #   3. POSTGRES_URL          – Vercel connection (may include PgBouncer)
    #   4. POSTGRES_PRISMA_URL   – Prisma-specific (includes pgbouncer=true)
    DATABASE_URL: Optional[str] = None
    POSTGRES_PRISMA_URL: Optional[str] = None

    @property
    def db_url(self) -> str:
        """
        Return a clean SQLAlchemy-compatible database URL.
        Prefers direct-connection URLs over PgBouncer-proxied ones,
        and strips any Prisma-specific query parameters.
        """
        raw = (
            self.DATABASE_URL
            or os.getenv("POSTGRES_URL_NON_POOLING")
            or os.getenv("POSTGRES_URL")
            or self.POSTGRES_PRISMA_URL
            or ""
        )
        return _clean_db_url(raw)

    # Security — SECRET_KEY must be set in production; fallback is dev-only
    SECRET_KEY: str = "dev-only-insecure-key-set-SECRET_KEY-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    # CORS
    FRONTEND_URL: str = "https://pikcarz.co.za"
    BACKEND_URL: str = "https://pikcarz.vercel.app"

    # Cloudinary — optional; image upload will be unavailable if not set
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # PayFast — optional; payments will be unavailable if not set
    PAYFAST_MERCHANT_ID: Optional[str] = None
    PAYFAST_MERCHANT_KEY: Optional[str] = None
    PAYFAST_PASSPHRASE: Optional[str] = None
    PAYFAST_MODE: str = "sandbox"

    # Cron job secret for renewal reminders
    CRON_SECRET: str = "pikcarz-cron-2026"

    # Admin
    ADMIN_EMAIL: str = "admin@pikcarz.co.za"
    ADMIN_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# PayFast URLs
PAYFAST_URL = (
    "https://www.payfast.co.za/eng/process"
    if settings.PAYFAST_MODE == "live"
    else "https://sandbox.payfast.co.za/eng/process"
)
