"""
Subscription and Payment API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.models import SubscriptionTier, PaymentStatus
from app.schemas.subscription import SubscriptionPlan, PaymentCreate, PaymentResponse, PayFastWebhook
from app.core.deps import get_current_user
from app.services.payfast import generate_payment_url, verify_payfast_signature
from app.config import settings

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions & Payments"])

# Define subscription plans
SUBSCRIPTION_PLANS = {
    "free": SubscriptionPlan(
        tier="free",
        name="Free",
        price=Decimal("0"),
        duration_days=30,
        max_listings=3,
        features=["3 active listings", "Basic support", "30-day expiry"]
    ),
    "standard": SubscriptionPlan(
        tier="standard",
        name="Standard",
        price=Decimal("299"),
        duration_days=30,
        max_listings=10,
        features=["10 active listings", "Email support", "Featured badge", "No ads"]
    ),
    "premium": SubscriptionPlan(
        tier="premium",
        name="Premium",
        price=Decimal("599"),
        duration_days=30,
        max_listings=25,
        features=["25 active listings", "Priority support", "Top placement", "Analytics", "No ads"]
    ),
    "dealer_basic": SubscriptionPlan(
        tier="dealer_basic",
        name="Dealer Basic",
        price=Decimal("1499"),
        duration_days=30,
        max_listings=50,
        features=["50 active listings", "Dealer badge", "Priority support", "Analytics"]
    ),
    "dealer_pro": SubscriptionPlan(
        tier="dealer_pro",
        name="Dealer Pro",
        price=Decimal("2999"),
        duration_days=30,
        max_listings=150,
        features=["150 active listings", "Verified dealer badge", "Featured placement", "Advanced analytics", "API access"]
    ),
    "dealer_enterprise": SubscriptionPlan(
        tier="dealer_enterprise",
        name="Dealer Enterprise",
        price=Decimal("5999"),
        duration_days=30,
        max_listings=9999,
        features=["Unlimited listings", "Verified dealer badge", "Premium placement", "Dedicated support", "API access", "Custom integrations"]
    )
}

@router.get("/plans", response_model=List[SubscriptionPlan])
def get_subscription_plans():
    """Get all available subscription plans"""
    return list(SUBSCRIPTION_PLANS.values())

@router.get("/plans/{tier}", response_model=SubscriptionPlan)
def get_subscription_plan(tier: str):
    """Get a specific subscription plan"""
    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    return SUBSCRIPTION_PLANS[tier]

@router.post("/subscribe", status_code=status.HTTP_200_OK)
def create_subscription(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate subscription payment with PayFast"""
    
    # Validate subscription tier
    if payment_data.subscription_tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    plan = SUBSCRIPTION_PLANS[payment_data.subscription_tier]
    
    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=plan.price,
        subscription_tier=SubscriptionTier(payment_data.subscription_tier),
        status=PaymentStatus.PENDING,
        item_name=plan.name,
        item_description=f"pikCarz {plan.name} Subscription - 30 days"
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Generate PayFast payment URL
    payment_url = generate_payment_url(
        amount=float(plan.price),
        item_name=plan.name,
        item_description=payment.item_description,
        email_address=current_user.email,
        name_first=current_user.full_name.split()[0] if current_user.full_name else "User",
        name_last=" ".join(current_user.full_name.split()[1:]) if len(current_user.full_name.split()) > 1 else "",
        m_payment_id=str(payment.id),
        user_id=current_user.id
    )
    
    return {
        "payment_id": payment.id,
        "payment_url": payment_url,
        "amount": plan.price,
        "subscription_tier": payment_data.subscription_tier
    }

@router.post("/webhook/payfast", status_code=status.HTTP_200_OK)
async def payfast_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayFast ITN (Instant Transaction Notification) webhook"""
    
    # Get form data from PayFast
    form_data = await request.form()
    data = dict(form_data)
    
    # Verify PayFast signature
    if not verify_payfast_signature(data):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Extract payment info
    m_payment_id = data.get("m_payment_id")
    pf_payment_id = data.get("pf_payment_id")
    payment_status = data.get("payment_status")
    
    if not m_payment_id:
        raise HTTPException(status_code=400, detail="Missing payment ID")
    
    # Find payment record
    payment = db.query(Payment).filter(Payment.id == int(m_payment_id)).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Update payment record
    payment.pf_payment_id = pf_payment_id
    payment.raw_webhook_data = str(data)
    
    if payment_status == "COMPLETE":
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()
        
        # Update user subscription
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            user.subscription_tier = payment.subscription_tier
            user.subscription_expires = datetime.utcnow() + timedelta(days=30)
    
    else:
        payment.status = PaymentStatus.FAILED
    
    db.commit()
    
    return {"status": "success"}

@router.get("/my/subscription", response_model=dict)
def get_my_subscription(
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription details"""
    
    plan = SUBSCRIPTION_PLANS.get(current_user.subscription_tier, SUBSCRIPTION_PLANS["free"])
    
    return {
        "current_plan": plan,
        "expires_at": current_user.subscription_expires,
        "is_active": current_user.subscription_expires and current_user.subscription_expires > datetime.utcnow() if current_user.subscription_expires else False
    }

@router.get("/my/payments", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all payments for current user"""
    
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
    return payments
