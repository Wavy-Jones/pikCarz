"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models import VehicleStatus, UserRole, PaymentStatus
from app.schemas.vehicle import VehicleResponse, VehicleListResponse, VehicleUpdate
from app.core.deps import get_current_admin
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _now_aware():
    """Return current UTC time as a timezone-aware datetime."""
    return datetime.now(tz=timezone.utc)


def _seller_name(vehicle, owner) -> str:
    if vehicle.contact_name:
        return vehicle.contact_name
    if owner:
        return owner.business_name or owner.full_name
    return "Unknown"


def _vehicle_response(vehicle, owner) -> VehicleResponse:
    now  = _now_aware()
    resp = VehicleResponse.model_validate(vehicle)
    resp.seller_name   = _seller_name(vehicle, owner)
    resp.seller_type   = owner.role if owner else "individual"
    resp.is_verified   = bool(owner.is_verified_dealer) if owner and owner.role == "dealer" else False
    resp.contact_name  = vehicle.contact_name or None
    resp.contact_phone = vehicle.contact_phone or None
    resp.seller_phone  = vehicle.contact_phone or (owner.phone if owner else None) or None
    resp.seller_email  = owner.email if owner else None
    # Referral badges
    resp.seller_is_founding_dealer = bool(owner.is_founding_dealer) if owner else False
    resp.seller_is_ambassador      = bool(owner.is_ambassador)      if owner else False
    resp.seller_priority_active    = bool(
        owner and owner.priority_search_until and owner.priority_search_until > now
    )
    return resp


def _purge_expired_admin_listings(db: Session):
    now = _now_aware()
    admin_ids = [row[0] for row in db.query(User.id).filter(User.role == UserRole.ADMIN).all()]
    if not admin_ids:
        return
    expired = db.query(Vehicle).filter(
        Vehicle.owner_id.in_(admin_ids),
        Vehicle.expires_at.isnot(None),
        Vehicle.expires_at < now,
    ).all()
    for v in expired:
        db.delete(v)
    if expired:
        db.commit()


@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_sold = db.execute(text("SELECT COUNT(*) FROM sold_vehicles")).scalar() or 0
    sold_this_month = db.execute(
        text("SELECT COUNT(*) FROM sold_vehicles WHERE sold_at >= DATE_TRUNC('month', NOW())")
    ).scalar() or 0
    return {
        "total_users":      db.query(User).count(),
        "total_vehicles":   db.query(Vehicle).count(),
        "active_vehicles":  db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count(),
        "pending_vehicles": db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING).count(),
        "total_dealers":    db.query(User).filter(User.role == UserRole.DEALER).count(),
        "verified_dealers": db.query(User).filter(
            User.role == UserRole.DEALER, User.is_verified_dealer == True
        ).count(),
        "total_sold":       int(total_sold),
        "sold_this_month":  int(sold_this_month),
    }


@router.post("/cleanup-sold-listings")
@router.get("/cleanup-sold-listings")
def cleanup_sold_listings(secret: str, db: Session = Depends(get_db)):
    """
    Called by a daily cron job. Permanently removes any vehicle listing that
    has been marked Sold for 7+ days — the sold_vehicles stats record stays
    forever, but the listing itself disappears from the seller's dashboard
    so the same car can't be re-listed or marked sold twice.
    """
    from app.config import settings
    if secret != settings.CRON_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    cutoff = _now_aware() - timedelta(days=7)
    expired_sold = db.query(Vehicle).filter(
        Vehicle.status == VehicleStatus.SOLD,
        Vehicle.sold_at.isnot(None),
        Vehicle.sold_at < cutoff,
    ).all()
    count = len(expired_sold)
    for v in expired_sold:
        db.delete(v)
    db.commit()
    return {"removed": count}


@router.get("/revenue")
def get_revenue(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        rows = db.execute(
            text("""
                SELECT
                    TO_CHAR(DATE_TRUNC('month', created_at), 'YYYY-MM') AS month,
                    SUM(amount)::float                                   AS total,
                    COUNT(*)                                             AS payments
                FROM payments
                WHERE status::text = 'completed'
                  AND created_at >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', created_at)
                ORDER BY DATE_TRUNC('month', created_at) DESC
            """)
        ).fetchall()

        all_time_row = db.execute(
            text("""
                SELECT COALESCE(SUM(amount), 0)::float AS total,
                       COUNT(*) AS payments
                FROM payments
                WHERE status::text = 'completed'
            """)
        ).fetchone()

        monthly = [
            {"month": row[0], "total": round(row[1], 2), "payments": int(row[2])}
            for row in rows
        ]

        return {
            "monthly": monthly,
            "all_time_total":    round(all_time_row[0], 2) if all_time_row else 0,
            "all_time_payments": int(all_time_row[1]) if all_time_row else 0,
        }
    except Exception as exc:
        import traceback
        print(f"[/api/admin/revenue] ERROR:\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"detail": str(exc)})


@router.get("/subscriptions")
def admin_get_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    try:
        now = _now_aware()
        offset = (page - 1) * per_page

        count_row = db.execute(
            text("SELECT COUNT(*) FROM users WHERE role::text != 'admin'")
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        user_rows = db.execute(
            text(
                "SELECT id, full_name, email, role::text, "
                "       subscription_tier::text, subscription_expires, is_verified_dealer "
                "FROM users "
                "WHERE role::text != 'admin' "
                "ORDER BY created_at DESC "
                "LIMIT :lim OFFSET :off"
            ),
            {"lim": per_page, "off": offset},
        ).fetchall()

        if not user_rows:
            return {"total": total, "page": page, "per_page": per_page, "users": []}

        user_ids = [row[0] for row in user_rows]
        id_params = {f"p{i}": uid for i, uid in enumerate(user_ids)}
        in_clause = ", ".join(f":p{i}" for i in range(len(user_ids)))

        pay_rows = db.execute(
            text(
                "SELECT DISTINCT ON (user_id) user_id, amount, created_at "
                f"FROM payments "
                f"WHERE user_id IN ({in_clause}) "
                f"  AND status::text = 'completed' "
                f"ORDER BY user_id, created_at DESC"
            ),
            id_params,
        ).fetchall()
        last_payment = {row[0]: {"amount": float(row[1]), "date": row[2]} for row in pay_rows}

        vcount_rows = db.execute(
            text(
                "SELECT owner_id, COUNT(*) AS cnt "
                f"FROM vehicles "
                f"WHERE owner_id IN ({in_clause}) "
                f"GROUP BY owner_id"
            ),
            id_params,
        ).fetchall()
        vcount = {row[0]: int(row[1]) for row in vcount_rows}

        results = []
        for row in user_rows:
            uid, full_name, email, role, sub_tier, sub_expires, is_verified = row
            is_active = bool(sub_expires and sub_expires > now)
            lp = last_payment.get(uid)
            results.append({
                "id":                   uid,
                "full_name":            full_name or "",
                "email":                email or "",
                "role":                 role or "individual",
                "subscription_tier":    sub_tier or "free",
                "subscription_expires": sub_expires.isoformat() if sub_expires else None,
                "is_active":            is_active,
                "last_payment_amount":  lp["amount"] if lp else None,
                "last_payment_date":    lp["date"].isoformat() if lp else None,
                "vehicle_count":        vcount.get(uid, 0),
                "is_verified_dealer":   bool(is_verified),
            })

        return {"total": total, "page": page, "per_page": per_page, "users": results}

    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"[/api/admin/subscriptions] ERROR:\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__},
        )


@router.get("/vehicles/all")
def admin_list_all_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    search: str = Query(None, description="Search by seller name, vehicle make, or model"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _purge_expired_admin_listings(db)
    from sqlalchemy import case, or_

    base_query = db.query(Vehicle)
    if search and search.strip():
        term = f"%{search.strip()}%"
        base_query = base_query.outerjoin(User, Vehicle.owner_id == User.id).filter(
            or_(
                Vehicle.make.ilike(term),
                Vehicle.model.ilike(term),
                Vehicle.title.ilike(term),
                Vehicle.contact_name.ilike(term),
                User.full_name.ilike(term),
                User.business_name.ilike(term),
                User.email.ilike(term),
            )
        )

    total  = base_query.with_entities(func.count(Vehicle.id)).scalar() or 0
    offset = (page - 1) * per_page
    vehicles = (
        base_query
        .order_by(
            # Pending listings float to the top, oldest pending first
            case(
                (Vehicle.status == VehicleStatus.PENDING, 0),
                else_=1
            ),
            # Within pending: oldest uploaded first (FIFO queue)
            # Within others: newest first
            Vehicle.created_at.asc()
        )
        .offset(offset).limit(per_page).all()
    )
    cache: dict = {}
    def _owner(oid):
        if oid not in cache:
            cache[oid] = db.query(User).filter(User.id == oid).first()
        return cache[oid]
    return VehicleListResponse(
        total=total, page=page, per_page=per_page,
        vehicles=[_vehicle_response(v, _owner(v.owner_id)) for v in vehicles],
    )


@router.get("/vehicles/pending", response_model=VehicleListResponse)
def get_pending_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str = Query(None, description="Search by seller name, vehicle make, or model"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _purge_expired_admin_listings(db)
    from sqlalchemy import or_
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.outerjoin(User, Vehicle.owner_id == User.id).filter(
            or_(
                Vehicle.make.ilike(term),
                Vehicle.model.ilike(term),
                Vehicle.title.ilike(term),
                Vehicle.contact_name.ilike(term),
                User.full_name.ilike(term),
                User.business_name.ilike(term),
                User.email.ilike(term),
            )
        )
    total  = query.with_entities(func.count(Vehicle.id)).scalar() or 0
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    cache: dict = {}
    def _owner(oid):
        if oid not in cache:
            cache[oid] = db.query(User).filter(User.id == oid).first()
        return cache[oid]
    return VehicleListResponse(
        total=total, page=page, per_page=per_page,
        vehicles=[_vehicle_response(v, _owner(v.owner_id)) for v in vehicles],
    )


@router.put("/vehicles/{vehicle_id}/approve", response_model=VehicleResponse)
def approve_vehicle(vehicle_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v: raise HTTPException(404, "Vehicle not found")
    if v.status not in (VehicleStatus.PENDING, VehicleStatus.REJECTED):
        raise HTTPException(400, f"Cannot approve a vehicle with status '{v.status}'")
    v.status = VehicleStatus.ACTIVE
    db.commit(); db.refresh(v)
    try:
        _notify_search_alerts(v, db)
    except Exception as e:
        print(f"[search_alerts] notification error: {e}")
    return _vehicle_response(v, db.query(User).filter(User.id == v.owner_id).first())


def _notify_search_alerts(vehicle: Vehicle, db: Session):
    from app.models.search_alert import SearchAlert
    from app.services.email import send_email
    alerts = db.query(SearchAlert).all()
    for alert in alerts:
        if alert.make     and alert.make.lower()     not in vehicle.make.lower():      continue
        if alert.category and alert.category          != vehicle.category.value:       continue
        if alert.province and alert.province.lower()  not in vehicle.province.lower(): continue
        if alert.min_price and float(vehicle.price) < float(alert.min_price):          continue
        if alert.max_price and float(vehicle.price) > float(alert.max_price):          continue
        user = db.query(User).filter(User.id == alert.user_id).first()
        if not user: continue
        detail_url = f"https://pikcarz.co.za/vehicle-detail.html?id={vehicle.id}"
        send_email(
            to=user.email,
            subject=f"New listing matches your alert: {vehicle.title}",
            body=(
                f"Hi {user.full_name},\n\n"
                f"A new vehicle matching your saved search is now available on pikCarz:\n\n"
                f"  {vehicle.title}\n"
                f"  R {float(vehicle.price):,.0f} · {vehicle.province}\n\n"
                f"View it here: {detail_url}\n\n"
                f"Happy hunting,\nThe pikCarz Team"
            )
        )


@router.put("/vehicles/{vehicle_id}/reject", response_model=VehicleResponse)
def reject_vehicle(vehicle_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v: raise HTTPException(404, "Vehicle not found")
    if v.status != VehicleStatus.PENDING: raise HTTPException(400, "Vehicle is not pending")
    v.status = VehicleStatus.REJECTED
    db.commit(); db.refresh(v)
    return _vehicle_response(v, db.query(User).filter(User.id == v.owner_id).first())


@router.put("/vehicles/{vehicle_id}/edit", response_model=VehicleResponse)
def admin_edit_vehicle(vehicle_id: int, vehicle_data: VehicleUpdate, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v: raise HTTPException(404, "Vehicle not found")
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(v, field, value)
    db.commit(); db.refresh(v)
    return _vehicle_response(v, db.query(User).filter(User.id == v.owner_id).first())


@router.delete("/vehicles/{vehicle_id}")
def admin_delete_vehicle(vehicle_id: int, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v: raise HTTPException(404, "Vehicle not found")
    db.delete(v); db.commit()
    return {"message": "Vehicle deleted"}


@router.delete("/users/{user_id}")
def admin_delete_user(user_id: int, current_admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.role == UserRole.ADMIN:
        raise HTTPException(403, "Cannot delete admin accounts")
    if user.id == current_admin.id:
        raise HTTPException(400, "Cannot delete your own account")
    db.delete(user)
    db.commit()
    return {"message": f"User {user.email} deleted"}


@router.put("/users/{user_id}/verify-dealer")
def admin_toggle_verified_dealer(
    user_id: int,
    verified: bool = Query(..., description="True to verify, False to revoke verification"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Manually verify (or revoke verification for) a dealer account.
    This is what actually sets `is_verified_dealer`, which drives the
    'Verified Dealers' stat card and the verified badge shown on listings.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if user.role != UserRole.DEALER:
        raise HTTPException(400, "Only dealer accounts can be verified")
    user.is_verified_dealer = verified
    db.commit()
    db.refresh(user)
    return {
        "message": f"{user.business_name or user.full_name} is now {'verified' if verified else 'unverified'}",
        "user_id": user.id,
        "is_verified_dealer": user.is_verified_dealer,
    }


@router.post("/broadcast")
def admin_broadcast_message(
    subject: str = Query(..., min_length=1, max_length=200),
    message: str = Query(..., min_length=1, max_length=4000),
    audience: str = Query("all", description="all | active_subscribers | dealers | free"),
    channels: str = Query("email,whatsapp", description="Comma-separated: email, whatsapp"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Send a single announcement (specials, important notices, downtime, etc.)
    to many users at once via email and/or WhatsApp — instead of contacting
    each subscriber one by one.

    audience options:
      all                 — every non-admin user
      active_subscribers  — users with a currently active paid subscription
      dealers              — users with role = dealer
      free                 — users on the free tier (e.g. to upsell)
    """
    from app.services.email import send_email
    from app.services.whatsapp import send_whatsapp_message

    now = _now_aware()
    query = db.query(User).filter(User.role != UserRole.ADMIN)

    if audience == "active_subscribers":
        query = query.filter(User.subscription_expires.isnot(None), User.subscription_expires > now)
    elif audience == "dealers":
        query = query.filter(User.role == UserRole.DEALER)
    elif audience == "free":
        from app.models import SubscriptionTier
        query = query.filter(User.subscription_tier == SubscriptionTier.FREE)
    elif audience != "all":
        raise HTTPException(400, f"Unknown audience '{audience}'")

    users = query.all()
    chosen_channels = {c.strip().lower() for c in channels.split(",") if c.strip()}

    emails_sent = 0
    whatsapps_sent = 0
    skipped_no_phone = 0

    for user in users:
        if "email" in chosen_channels and user.email:
            body = f"Hi {user.full_name},\n\n{message}\n\n— The pikCarz Team"
            if send_email(to=user.email, subject=subject, body=body):
                emails_sent += 1

        if "whatsapp" in chosen_channels:
            if user.phone:
                wa_message = f"*{subject}*\n\n{message}\n\n— pikCarz"
                if send_whatsapp_message(to_phone=user.phone, message=wa_message):
                    whatsapps_sent += 1
            else:
                skipped_no_phone += 1

    return {
        "message": f"Broadcast sent to {len(users)} user(s).",
        "audience": audience,
        "users_targeted": len(users),
        "emails_sent": emails_sent,
        "whatsapps_sent": whatsapps_sent,
        "skipped_no_phone": skipped_no_phone,
    }
