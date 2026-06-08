"""
Referral API — user-facing stats + admin management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.user import User
from app.models.referral import Referral
from app.core.deps import get_current_user, get_current_admin
import secrets

router = APIRouter(prefix="/api/referrals", tags=["Referrals"])

SITE_URL = "https://pikcarz.co.za"


def _generate_code() -> str:
    """Generate a short unique referral code."""
    return secrets.token_hex(4).upper()   # 8-char e.g. "A3F8C21D"


def _apply_milestones(user: User, db: Session):
    """Auto-award Founding Dealer badge at 3 referrals and Ambassador at 10."""
    changed = False
    if user.referral_count >= 3 and not user.is_founding_dealer:
        user.is_founding_dealer = True
        changed = True
    if user.referral_count >= 10 and not user.is_ambassador:
        user.is_ambassador = True
        changed = True
    if changed:
        db.commit()
        db.refresh(user)


# ── User endpoints ─────────────────────────────────────────────────────────────

@router.get("/my-stats")
def get_my_referral_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current user's referral link, count, badges and next milestone."""
    now = datetime.now(tz=timezone.utc)

    referrals = db.query(Referral).filter(Referral.referrer_id == current_user.id).all()
    recent = sorted(referrals, key=lambda r: r.created_at, reverse=True)[:5]

    # Next milestone
    count = current_user.referral_count
    if count < 1:
        next_milestone = {"target": 1, "reward": "Priority Search Placement for 7 days"}
    elif count < 3:
        next_milestone = {"target": 3, "reward": "Founding Dealer Badge"}
    elif count < 5:
        next_milestone = {"target": 5, "reward": "Featured Homepage Listing for 14 days"}
    elif count < 10:
        next_milestone = {"target": 10, "reward": "PikCarz Ambassador Status"}
    else:
        next_milestone = None

    return {
        "referral_link":        f"{SITE_URL}/register.html?ref={current_user.referral_code}",
        "referral_code":        current_user.referral_code,
        "referral_count":       count,
        "is_founding_dealer":   current_user.is_founding_dealer,
        "is_ambassador":        current_user.is_ambassador,
        "priority_search_active": (
            current_user.priority_search_until is not None
            and current_user.priority_search_until > now
        ),
        "priority_search_until": current_user.priority_search_until,
        "featured_listing_active": (
            current_user.featured_listing_until is not None
            and current_user.featured_listing_until > now
        ),
        "featured_listing_until": current_user.featured_listing_until,
        "next_milestone":       next_milestone,
        "recent_referrals":     [{"id": r.referred_id, "date": r.created_at} for r in recent],
    }


# ── Admin endpoints ────────────────────────────────────────────────────────────

@router.get("/admin/leaderboard")
def referral_leaderboard(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Top referrers — for the admin dashboard."""
    rows = db.execute(text("""
        SELECT u.id, u.full_name, u.email, u.referral_count,
               u.is_founding_dealer, u.is_ambassador,
               u.priority_search_until, u.featured_listing_until
        FROM users u
        WHERE u.referral_count > 0
        ORDER BY u.referral_count DESC
        LIMIT 50
    """)).fetchall()

    now = datetime.now(tz=timezone.utc)
    return [
        {
            "id":                    r[0],
            "full_name":             r[1],
            "email":                 r[2],
            "referral_count":        r[3],
            "is_founding_dealer":    r[4],
            "is_ambassador":         r[5],
            "priority_search_until": r[6].isoformat() if r[6] else None,
            "priority_search_active": bool(r[6] and r[6] > now),
            "featured_listing_until": r[7].isoformat() if r[7] else None,
            "featured_listing_active": bool(r[7] and r[7] > now),
        }
        for r in rows
    ]


@router.post("/admin/grant-priority/{user_id}")
def grant_priority_search(
    user_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Grant 7-day priority search placement to a user (1 referral reward)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    now = datetime.now(tz=timezone.utc)
    # If already active, extend from current expiry; otherwise start from now
    base = user.priority_search_until if (user.priority_search_until and user.priority_search_until > now) else now
    user.priority_search_until = base + timedelta(days=7)
    db.commit()
    return {"message": f"Priority search granted until {user.priority_search_until.date()}", "until": user.priority_search_until}


@router.post("/admin/grant-featured/{user_id}")
def grant_featured_listing(
    user_id: int,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Grant 14-day homepage featured listing to a user (5 referral reward)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    now = datetime.now(tz=timezone.utc)
    base = user.featured_listing_until if (user.featured_listing_until and user.featured_listing_until > now) else now
    user.featured_listing_until = base + timedelta(days=14)
    db.commit()
    return {"message": f"Featured listing granted until {user.featured_listing_until.date()}", "until": user.featured_listing_until}
