"""
Subscription and Payment Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class SubscriptionPlan(BaseModel):
    tier: str  # free, standard, premium, dealer_basic, dealer_pro, dealer_enterprise
    name: str
    price: Decimal
    duration_days: int
    max_listings: int
    features: list

class PaymentCreate(BaseModel):
    subscription_tier: str
    amount: Decimal
    
class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    subscription_tier: str
    status: str
    payment_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PayFastWebhook(BaseModel):
    """PayFast ITN (Instant Transaction Notification) webhook"""
    m_payment_id: str
    pf_payment_id: str
    payment_status: str
    item_name: str
    item_description: Optional[str]
    amount_gross: str
    amount_fee: str
    amount_net: str
    merchant_id: str
    signature: str
