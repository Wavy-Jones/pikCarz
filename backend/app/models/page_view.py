"""
PageView model — tracks every page load on pikcarz.co.za
No IP addresses stored (POPIA compliance).
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class PageView(Base):
    __tablename__ = "page_views"

    id         = Column(Integer, primary_key=True, index=True)
    page_url   = Column(Text, nullable=False)          # e.g. /browse.html
    page_title = Column(String(255), nullable=True)
    referrer   = Column(Text, nullable=True)            # previous URL / source
    device_type = Column(String(20), nullable=True)    # mobile | desktop | tablet
    session_id  = Column(String(64), nullable=True)    # ephemeral, from sessionStorage
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now(), index=True)
