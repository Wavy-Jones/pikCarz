"""
User model
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models import UserRole, SubscriptionTier
import secrets


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name       = Column(String, nullable=False)
    phone           = Column(String, nullable=True)

    # User type
    role = Column(Enum(UserRole), default=UserRole.INDIVIDUAL, nullable=False)

    # Subscription
    subscription_tier    = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    subscription_expires = Column(DateTime(timezone=True), nullable=True)

    # Dealer-specific
    business_name         = Column(String,  nullable=True)
    business_registration = Column(String,  nullable=True)
    dealer_address        = Column(String,  nullable=True)
    is_verified_dealer    = Column(Boolean, default=False)

    # ── Referral system ───────────────────────────────────────
    referral_code          = Column(String(16), unique=True, nullable=True, index=True)
    referred_by            = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    referral_count         = Column(Integer, default=0, nullable=False)
    is_founding_dealer     = Column(Boolean, default=False)   # auto-awarded at 3 referrals
    is_ambassador          = Column(Boolean, default=False)   # auto-awarded at 10 referrals
    priority_search_until  = Column(DateTime(timezone=True), nullable=True)  # 7-day boost (admin-granted)
    featured_listing_until = Column(DateTime(timezone=True), nullable=True)  # 14-day feature (admin-granted)

    # Status
    is_active    = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    vehicles      = relationship("Vehicle",     back_populates="owner")
    favourites    = relationship("Favourite",   back_populates="user", cascade="all, delete-orphan")
    search_alerts = relationship("SearchAlert", back_populates="user", cascade="all, delete-orphan")
    payments      = relationship("Payment",     back_populates="user")
