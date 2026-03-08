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
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # CORS
    FRONTEND_URL: str = "https://wavy-jones.github.io/pikCarz"
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    # PayFast
    PAYFAST_MERCHANT_ID: str
    PAYFAST_MERCHANT_KEY: str
    PAYFAST_PASSPHRASE: str
    PAYFAST_MODE: str = "sandbox"  # or 'live'
    
    # Admin
    ADMIN_EMAIL: str = "admin@pikcarz.co.za"
    ADMIN_PASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# PayFast URLs
PAYFAST_URL = "https://www.payfast.co.za/eng/process" if settings.PAYFAST_MODE == "live" else "https://sandbox.payfast.co.za/eng/process"
