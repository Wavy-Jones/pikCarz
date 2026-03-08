"""
Payment model
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models import PaymentStatus, SubscriptionTier

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    subscription_tier = Column(Enum(SubscriptionTier), nullable=False)
    
    # PayFast
    payment_id = Column(String, unique=True, nullable=True)  # PayFast payment_id
    pf_payment_id = Column(String, nullable=True)  # PayFast pf_payment_id
    merchant_id = Column(String, nullable=True)
    
    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Metadata
    item_name = Column(String, nullable=True)
    item_description = Column(String, nullable=True)
    raw_webhook_data = Column(Text, nullable=True)  # Store full webhook JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
