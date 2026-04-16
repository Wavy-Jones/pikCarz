"""
Subscription and Payment API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request
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

# ── Plan definitions ──────────────────────────────────────────────────────────
# trial_days: how many FREE days a first-time subscriber gets before paying.
#             0 = no trial.  Premium gets 90 days (3 months), all others 30 days.
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free Tier",
        "price": 0,
        "duration_days": 30,
        "max_listings": 1,
        "trial_days": 0,
        "features": [
            "1 active listing",
            "30-day duration",
            "Basic visibility",
        ],
    },
    "standard": {
        "name": "Standard Plan",
        "price": 199,
        "duration_days": 30,
        "max_listings": 5,
        "trial_days": 30,
        "features": [
            "1 month FREE for new subscribers",
            "5 active listings",
            "60-day listing duration",
            "Featured placement",
            "Priority support",
        ],
    },
    "premium": {
        "name": "Premium Plan",
        "price": 499,
        "duration_days": 30,
        "max_listings": 15,
        "trial_days": 90,
        "features": [
            "3 months FREE for new subscribers",
            "15 active listings",
            "90-day listing duration",
            "Top featured placement",
            "Premium badge",
            "Priority support",
            "Analytics dashboard",
            "Lead tracking (calls & messages)",
        ],
    },
    "dealer_basic": {
        "name": "Dealer Basic",
        "price": 999,
        "duration_days": 30,
        "max_listings": 50,
        "trial_days": 30,
        "features": [
            "1 month FREE for new subscribers",
            "50 active listings",
            "Unlimited listing duration",
            "Verified dealer badge",
            "Bulk upload",
            "Advanced analytics",
            "Dedicated support",
            "Lead management dashboard",
        ],
    },
    "dealer_pro": {
        "name": "Dealer Pro",
        "price": 1999,
        "duration_days": 30,
        "max_listings": 200,
        "trial_days": 30,
        "features": [
            "1 month FREE for new subscribers",
            "200 active listings",
            "Unlimited listing duration",
            "Verified dealer badge",
            "Bulk upload",
            "Advanced analytics",
            "Priority placement",
            "Dedicated account manager",
            "Lead management dashboard",
        ],
    },
}


@router.get("/plans", response_model=List[SubscriptionPlan])
def get_subscription_plans():
    """Get all available subscription plans."""
    plans = []
    for tier, details in SUBSCRIPTION_PLANS.items():
        plans.append(SubscriptionPlan(
            tier=tier,
            name=details["name"],
            price=details["price"],
            duration_days=details["duration_days"],
            max_listings=details["max_listings"],
            features=details["features"],
        ))
    return plans


@router.post("/subscribe/{tier}")
async def subscribe_to_plan(
    tier: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a plan.
    - First-time subscribers receive a free trial (no payment required):
        Premium  → 3 months (90 days) free
        Others   → 1 month  (30 days) free
    - Returning subscribers are redirected to PayFast for payment.
    """
    if tier not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")

    plan = SUBSCRIPTION_PLANS[tier]

    # Free tier — instant activation, no payment ever needed
    if tier == "free":
        current_user.subscription_tier = SubscriptionTier.FREE
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=30)
        db.commit()
        return {
            "message": "Free tier activated",
            "tier": tier,
            "expires": current_user.subscription_expires,
        }

    # Check whether this user has ever completed a payment (trial eligibility)
    has_prior_payment = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id, Payment.status == PaymentStatus.COMPLETED)
        .first()
    ) is not None

    trial_days = plan.get("trial_days", 0)
    if not has_prior_payment and trial_days > 0:
        # Grant the free trial immediately — no PayFast redirect
        current_user.subscription_tier = SubscriptionTier(tier)
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=trial_days)
        db.commit()
        trial_label = "3 months" if trial_days == 90 else "1 month"
        return {
            "message": f"🎉 Free trial activated! You have {trial_label} of {plan['name']} at no charge.",
            "tier": tier,
            "expires": current_user.subscription_expires,
            "is_trial": True,
        }

    # Returning subscriber — go through PayFast payment
    payment = Payment(
        user_id=current_user.id,
        amount=plan["price"],
        subscription_tier=SubscriptionTier(tier),
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_url = generate_payment_url(
        payment_id=payment.id,
        amount=plan["price"],
        item_name=plan["name"],
        user_email=current_user.email,
        user_name=current_user.full_name,
    )

    return {
        "payment_url": payment_url,
        "payment_id": payment.id,
        "amount": plan["price"],
        "tier": tier,
    }


@router.post("/webhook/payfast")
async def payfast_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle PayFast ITN webhook."""
    form_data = await request.form()
    data = dict(form_data)

    if not verify_payfast_signature(data):
        raise HTTPException(status_code=400, detail="Invalid signature")

    payment_id = int(data.get("m_payment_id", 0))
    payment_status = data.get("payment_status")
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment_status == "COMPLETE":
        payment.status = PaymentStatus.COMPLETED
        payment.payfast_payment_id = data.get("pf_payment_id")
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
    """Get current user's subscription info."""
    return {
        "tier": current_user.subscription_tier.value,
        "expires": current_user.subscription_expires,
        "is_active": (
            current_user.subscription_expires > datetime.utcnow()
            if current_user.subscription_expires else False
        ),
    }


@router.get("/payments", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment history for current user."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return [PaymentResponse.model_validate(p) for p in payments]
