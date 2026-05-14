"""
User model
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models import UserRole, SubscriptionTier

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    
    # User type
    role = Column(Enum(UserRole), default=UserRole.INDIVIDUAL, nullable=False)
    
    # Subscription
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    subscription_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Dealer-specific
    business_name = Column(String, nullable=True)
    business_registration = Column(String, nullable=True)
    is_verified_dealer = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vehicles      = relationship("Vehicle",     back_populates="owner")
    favourites     = relationship("Favourite",   back_populates="user", cascade="all, delete-orphan")
    search_alerts  = relationship("SearchAlert", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user")
