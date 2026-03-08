"""
Database models
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    INDIVIDUAL = "individual"
    DEALER = "dealer"
    ADMIN = "admin"

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    DEALER_BASIC = "dealer_basic"
    DEALER_PRO = "dealer_pro"
    DEALER_ENTERPRISE = "dealer_enterprise"

class VehicleCategory(str, enum.Enum):
    NEW_CAR = "new_car"
    USED_CAR = "used_car"
    MOTORBIKE = "motorbike"
    TRUCK = "truck"
    OTHER = "other"

class VehicleStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    REJECTED = "rejected"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
