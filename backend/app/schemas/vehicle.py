"""
Vehicle Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class VehicleBase(BaseModel):
    make: str
    model: str
    year: int = Field(..., ge=1900, le=2030)
    category: str  # new_car, used_car, motorbike, truck, other
    price: Decimal = Field(..., gt=0)
    mileage: Optional[int] = Field(None, ge=0)
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    color: Optional[str] = None
    title: str
    description: Optional[str] = None
    province: str
    city: Optional[str] = None

class VehicleCreate(VehicleBase):
    images: Optional[List[str]] = []
    report_url: Optional[str] = None       # optional inspection/service report
    contact_name:  Optional[str] = None    # admin on-behalf override
    contact_phone: Optional[str] = None

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price: Optional[Decimal] = None
    mileage: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    color: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    images: Optional[List[str]] = None
    report_url: Optional[str] = None       # None = no change; "" = clear
    contact_name:  Optional[str] = None
    contact_phone: Optional[str] = None

class VehicleResponse(VehicleBase):
    id: int
    owner_id: int
    images: List[str]
    report_url: Optional[str] = None
    status: str
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]

    # Seller info
    seller_name:  Optional[str] = None
    seller_phone: Optional[str] = None
    seller_email: Optional[str] = None
    seller_type:  Optional[str] = None
    is_verified:  Optional[bool] = None
    contact_name:  Optional[str] = None
    contact_phone: Optional[str] = None

    # Engagement
    views:          int = 0
    whatsapp_leads: int = 0
    email_leads:    int = 0

    class Config:
        from_attributes = True

class VehicleListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    vehicles: List[VehicleResponse]
