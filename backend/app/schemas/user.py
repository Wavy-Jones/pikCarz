"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = "individual"  # individual or dealer
    business_name: Optional[str] = None
    business_registration: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str
    subscription_tier: str
    subscription_expires: Optional[datetime]
    business_name: Optional[str]
    is_verified_dealer: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
