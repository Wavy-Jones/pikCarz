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
    transmission: Optional[str] = None  # Auto, Manual, Semi-Auto
    fuel_type: Optional[str] = None  # Petrol, Diesel, Electric, Hybrid
    color: Optional[str] = None
    title: str
    description: Optional[str] = None
    province: str
    city: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

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

class VehicleResponse(VehicleBase):
    id: int
    owner_id: int
    images: List[str]
    status: str
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    # Seller info
    seller_name: Optional[str] = None
    seller_type: Optional[str] = None
    is_verified: Optional[bool] = None
    
    class Config:
        from_attributes = True

class VehicleListResponse(BaseModel):
    total: int
    page: int
    per_page: int
    vehicles: List[VehicleResponse]
