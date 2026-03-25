"""
pikCarz Backend Configuration
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "pikCarz API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Database (Vercel creates POSTGRES_PRISMA_URL automatically)
    DATABASE_URL: Optional[str] = None
    POSTGRES_PRISMA_URL: Optional[str] = None
    
    @property
    def db_url(self) -> str:
        """Get database URL, preferring POSTGRES_PRISMA_URL from Vercel"""
        return self.POSTGRES_PRISMA_URL or self.DATABASE_URL or ""
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # CORS
    FRONTEND_URL: str = "https://pikcarz.co.za"
    BACKEND_URL: str = "https://pikcarz.vercel.app"
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # PayFast
    PAYFAST_MERCHANT_ID: str
    PAYFAST_MERCHANT_KEY: str
    PAYFAST_PASSPHRASE: str
    PAYFAST_MODE: str = "live"  # Production mode - site is going live!
    
    # Admin
    ADMIN_EMAIL: str = "admin@pikcarz.co.za"
    ADMIN_PASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# PayFast URLs
PAYFAST_URL = "https://www.payfast.co.za/eng/process" if settings.PAYFAST_MODE == "live" else "https://sandbox.payfast.co.za/eng/process"
