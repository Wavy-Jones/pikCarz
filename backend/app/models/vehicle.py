"""
Vehicle model
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models import VehicleCategory, VehicleStatus

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic info
    make = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    category = Column(Enum(VehicleCategory), nullable=False, index=True)
    
    # Details
    price = Column(Numeric(12, 2), nullable=False)
    mileage = Column(Integer, nullable=True)
    transmission = Column(String, nullable=True)  # Auto/Manual
    fuel_type = Column(String, nullable=True)  # Petrol/Diesel/Electric/Hybrid
    color = Column(String, nullable=True)
    
    # Description
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Images (Cloudinary URLs as JSON array)
    images = Column(JSON, default=list)
    
    # Custom contact details (set by admin when listing on behalf of a seller)
    contact_name  = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    
    # Location
    province = Column(String, nullable=False)
    city = Column(String, nullable=True)
    
    # Status
    status = Column(Enum(VehicleStatus), default=VehicleStatus.PENDING, nullable=False, index=True)
    is_featured = Column(Boolean, default=False)
    
    # Engagement counters
    views        = Column(Integer, default=0, server_default='0', nullable=False)
    whatsapp_leads = Column(Integer, default=0, server_default='0', nullable=False)
    email_leads    = Column(Integer, default=0, server_default='0', nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="vehicles")
