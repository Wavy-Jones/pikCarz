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
from app.services.payfast import generate_payment_data, verify_payfast_signature
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])

# ── Plan definitions ──────────────────────────────────────────────────────────
# trial_days: free days a FIRST-TIME subscriber gets.
#   Premium      → 2 months (60 days)
#   Dealer Basic → 3 months (90 days)
#   Dealer Pro   → 3 months (90 days)
#   Standard     → 1 month  (30 days)
#   Free         → 0 (no trial; it's already free)
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
        "trial_days": 60,   # 2 months free
        "features": [
            "2 months FREE for new subscribers",
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
        "trial_days": 90,   # 3 months free
        "features": [
            "3 months FREE for new subscribers",
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
        "trial_days": 90,   # 3 months free
        "features": [
            "3 months FREE for new subscribers",
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


def _is_trial_eligible(user: User, db: Session) -> bool:
    """
    A user is eligible for a free trial ONLY if ALL of the following are true:
      1. They have never completed a payment on this account.
      2. Their current subscription_tier is FREE — meaning they have never
         previously activated a paid/trial subscription on this account.

    This dual-check prevents trial abuse via:
      - Creating a new account with the same email (blocked by DB unique constraint).
      - Re-subscribing after a trial expires without paying (tier stays non-FREE).
    """
    has_prior_payment = (
        db.query(Payment)
        .filter(Payment.user_id == user.id, Payment.status == PaymentStatus.COMPLETED)
        .first()
    ) is not None

    # If the user's tier is not FREE they have already used a trial before
    tier_is_free = user.subscription_tier == SubscriptionTier.FREE

    return (not has_prior_payment) and tier_is_free


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
    - Eligible first-time subscribers receive a free trial (no payment required).
    - Returning / previously-trialled subscribers go straight to PayFast.
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

    trial_days = plan.get("trial_days", 0)
    if trial_days > 0 and _is_trial_eligible(current_user, db):
        # Grant the free trial immediately — no PayFast redirect
        current_user.subscription_tier = SubscriptionTier(tier)
        current_user.subscription_expires = datetime.utcnow() + timedelta(days=trial_days)
        db.commit()
        if trial_days == 90:
            trial_label = "3 months"
        elif trial_days == 60:
            trial_label = "2 months"
        else:
            trial_label = "1 month"
        return {
            "message": f"🎉 Free trial activated! You have {trial_label} of {plan['name']} at no charge.",
            "tier": tier,
            "expires": current_user.subscription_expires,
            "is_trial": True,
        }

    # Returning / previously-trialled subscriber — go through PayFast payment
    payment = Payment(
        user_id=current_user.id,
        amount=plan["price"],
        subscription_tier=SubscriptionTier(tier),
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment_info = generate_payment_data(
        payment_id=payment.id,
        amount=plan["price"],
        item_name=plan["name"],
        user_email=current_user.email,
        user_name=current_user.full_name,
    )

    return {
        "payment_url": payment_info["url"],
        "payment_params": payment_info["params"],
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
        payment.pf_payment_id = data.get("pf_payment_id")
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            user.subscription_tier = payment.subscription_tier
            user.subscription_expires = datetime.utcnow() + timedelta(days=30)
    else:
        payment.status = PaymentStatus.FAILED

    db.commit()
    return {"status": "ok"}


@router.post("/send-renewal-reminders")
def send_renewal_reminders(secret: str, db: Session = Depends(get_db)):
    """Called by a cron job to send subscription renewal reminder emails."""
    from app.config import settings
    from app.services.email import send_email
    if secret != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    now = datetime.utcnow()
    reminder_window = now + timedelta(days=7)
    users = db.query(User).filter(
        User.subscription_expires != None,
        User.subscription_expires > now,
        User.subscription_expires <= reminder_window,
        User.subscription_tier != SubscriptionTier.FREE,
    ).all()
    sent = 0
    for user in users:
        days_left = (user.subscription_expires.replace(tzinfo=None) - now).days
        tier_name = user.subscription_tier.value.replace('_', ' ').title()
        send_email(
            to=user.email,
            subject=f"Your pikCarz {tier_name} subscription expires in {days_left} day(s)",
            body=(
                f"Hi {user.full_name},\n\n"
                f"Your {tier_name} subscription on pikCarz expires in {days_left} day(s).\n\n"
                f"To keep your listings active and avoid interruption, "
                f"please renew by visiting:\n"
                f"https://pikcarz.co.za/dashboard.html\n\n"
                f"Thank you for being part of pikCarz!\n"
                f"The pikCarz Team"
            )
        )
        sent += 1
    return {"reminders_sent": sent}


@router.get("/my-subscription")
def get_my_subscription(current_user: User = Depends(get_current_user)):
    """Get current user's subscription info."""
    return {
        "tier": current_user.subscription_tier.value,
        "expires": current_user.subscription_expires,
        "is_active": (
            current_user.subscription_expires.replace(tzinfo=None) > datetime.utcnow()
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
