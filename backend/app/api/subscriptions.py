"""
Subscription and Payment API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.models import SubscriptionTier, PaymentStatus
from app.schemas.subscription import SubscriptionPlan, PaymentCreate, PaymentResponse, PayFastWebhook
from app.core.deps import get_current_user
from app.services.payfast import generate_payment_url, verify_payfast_signature
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free Tier",
        "price": 0,
        "duration_days": 30,
        "max_listings": 1,
        "features": [
            "1 active listing",
            "30-day duration",
            "Basic visibility"
        ]
    },
    "standard": {
        "name": "Standard Plan",
        "price": 199,  # R199/month
        "duration_days": 30,
        "max_listings": 5,
        "features": [
            "5 active listings",
            "60-day duration",
            "Featured placement",
            "Priority support"
        ]
    },
    "premium": {
        "name": "Premium Plan",
        "price": 499,  # R499/month
        "duration_days": 30,
        "max_listings": 15,
        "features": [
            "15 active listings",
            "90-day duration",
            "Top featured placement",
            "Premium badge",
            "Priority support",
            "Analytics dashboard",
            "Lead tracking (calls & messages)"
        ]
    },
    "dealer_basic": {
        "name": "Dealer Basic",
        "price": 999,  # R999/month
        "duration_days": 30,
        "max_listings": 50,
        "features": [
            "50 active listings",
            "Unlimited duration",
            "Verified dealer badge",
            "Bulk upload",
            "Advanced analytics",
            "Dedicated support",
            "Lead management dashboard"
        ]
    },
    "dealer_pro": {
        "name": "Dealer Pro",
        "price": 1999,  # R1,999/month — increases to R2,399 after first 100 subscribers
        "duration_days": 30,
        "max_listings": 200,
        "features": [
            "200 active listings",
            "Unlimited duration",
            "Verified dealer badge",
            "Bulk upload",
            "Advanced analytics",
            "Priority placement",
            "Dedicated account manager",
            "Lead management dashboard"
        ]
    }
}

@router.get("/plans", response_model=List[SubscriptionPlan])
def get_subscription_plans():
    """Get all available subscription plans"""
    plans = []
    for tier, details in SUBSCRIPTION_PLANS.items():
        plans.append(SubscriptionPlan(
            tier=tier,
            name=details["name"],
            price=details["price"],
            duration_days=details["duration_days"],
            max_listings=details["max_listings"],
            features=details["features"]
        ))
    return plans

@router.post("/subscribe/{tier}")
async def subscribe_to_plan(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe to a plan - generates PayFast payment URL"""
    
    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    plan = SUBSCRIPTION_PLANS[tier]
    
    # Free tier - instant activation
    if tier == "free":
        current_user.subscription_tier = SubscriptionTier.FREE
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        db.commit()
        
        return {
            "message": "Free tier activated",
            "tier": tier,
            "expires": current_user.subscription_expires
        }
    
    # Create payment record
    payment = Payment(
        user_id=current_user.id,
        amount=plan["price"],
        subscription_tier=SubscriptionTier(tier),
        status=PaymentStatus.PENDING
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    # Generate PayFast payment URL
    payment_url = generate_payment_url(
        payment_id=payment.id,
        amount=plan["price"],
        item_name=plan["name"],
        user_email=current_user.email,
        user_name=current_user.full_name
    )
    
    return {
        "payment_url": payment_url,
        "payment_id": payment.id,
        "amount": plan["price"],
        "tier": tier
    }

@router.post("/webhook/payfast")
async def payfast_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayFast ITN (Instant Transaction Notification) webhook"""
    
    # Get form data
    form_data = await request.form()
    data = dict(form_data)
    
    # Verify PayFast signature
    if not verify_payfast_signature(data):
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Extract payment info
    payment_id = int(data.get('m_payment_id', 0))
    payment_status = data.get('payment_status')
    
    # Get payment record
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Update payment status
    if payment_status == "COMPLETE":
        payment.status = PaymentStatus.COMPLETED
        payment.payfast_payment_id = data.get('pf_payment_id')
        
        # Update user subscription
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            user.subscription_tier = payment.subscription_tier
            user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        
    else:
        payment.status = PaymentStatus.FAILED
    
    db.commit()
    
    return {"status": "ok"}

@router.get("/my-subscription")
def get_my_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription info"""
    
    return {
        "tier": current_user.subscription_tier.value,
        "expires": current_user.subscription_expires,
        "is_active": current_user.subscription_expires > datetime.utcnow() if current_user.subscription_expires else False
    }

@router.get("/payments", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for current user"""
    
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).order_by(Payment.created_at.desc()).all()
    
    return [PaymentResponse.model_validate(p) for p in payments]
