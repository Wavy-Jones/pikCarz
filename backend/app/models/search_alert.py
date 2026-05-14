"""
Search alert model
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SearchAlert(Base):
    __tablename__ = "search_alerts"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    make       = Column(String,  nullable=True)
    category   = Column(String,  nullable=True)
    province   = Column(String,  nullable=True)
    min_price  = Column(Numeric(12, 2), nullable=True)
    max_price  = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="search_alerts")
