"""
Admin API routes - Approve/reject vehicles, manage users & subscriptions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.payment import Payment
from app.models import VehicleStatus, UserRole, PaymentStatus
from app.schemas.vehicle import VehicleResponse, VehicleListResponse, VehicleUpdate
from app.core.deps import get_current_admin
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# Helpers

def _seller_name(vehicle: Vehicle, owner: User | None) -> str:
    """Use contact_name when the admin listed on behalf of someone."""
    if vehicle.contact_name:
        return vehicle.contact_name
    if owner:
        return owner.business_name or owner.full_name
    return "Unknown"


def _vehicle_response(vehicle: Vehicle, owner: User | None) -> VehicleResponse:
    resp = VehicleResponse.model_validate(vehicle)
    resp.seller_name  = _seller_name(vehicle, owner)
    resp.seller_type  = owner.role if owner else "individual"
    resp.is_verified  = bool(owner.is_verified_dealer) if owner and owner.role == "dealer" else False
    resp.contact_name  = vehicle.contact_name  or None
    resp.contact_phone = vehicle.contact_phone or None
    return resp


def _purge_expired_admin_listings(db: Session):
    """
    Delete any listing created by an admin that has passed its expires_at.
    Called lazily from admin list endpoints so no background job is needed.
    """
    now = datetime.utcnow()
    admin_ids = [u.id for u in db.query(User.id).filter(User.role == UserRole.ADMIN).all()]
    if not admin_ids:
        return
    expired = db.query(Vehicle).filter(
        Vehicle.owner_id.in_(admin_ids),
        Vehicle.expires_at != None,
        Vehicle.expires_at < now,
    ).all()
    for v in expired:
        db.delete(v)
    if expired:
        db.commit()


# Stats

@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return {
        "total_users":      db.query(User).count(),
        "total_vehicles":   db.query(Vehicle).count(),
        "active_vehicles":  db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count(),
        "pending_vehicles": db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING).count(),
        "total_dealers":    db.query(User).filter(User.role == UserRole.DEALER).count(),
        "verified_dealers": db.query(User).filter(User.role == UserRole.DEALER, User.is_verified_dealer == True).count(),
    }


# Subscriptions Overview
# FIXED: replaced N+1 queries (1 payment query + 1 vehicle count per user) with
# 3 subqueries joined in a single round-trip. This prevents Vercel's 10-second
# serverless timeout from causing "Failed to fetch" on the admin dashboard.

@router.get("/subscriptions")
def admin_get_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: view all users and their subscription status.
    Uses aggregated subqueries instead of N+1 queries to avoid Vercel timeouts.
    """
    now = datetime.utcnow()

    # Subquery 1: most recent completed-payment date per user
    last_pay_date_sq = (
        db.query(
            Payment.user_id,
            func.max(Payment.created_at).label("last_date"),
        )
        .filter(Payment.status == PaymentStatus.COMPLETED)
        .group_by(Payment.user_id)
        .subquery()
    )

    # Subquery 2: join back to get the amount for that date
    last_pay_sq = (
        db.query(
            Payment.user_id,
            Payment.amount.label("last_payment_amount"),
            Payment.created_at.label("last_payment_date"),
        )
        .join(
            last_pay_date_sq,
            (Payment.user_id == last_pay_date_sq.c.user_id)
            & (Payment.created_at == last_pay_date_sq.c.last_date)
            & (Payment.status == PaymentStatus.COMPLETED),
        )
        .subquery()
    )

    # Subquery 3: vehicle count per owner
    vcount_sq = (
        db.query(
            Vehicle.owner_id,
            func.count(Vehicle.id).label("vehicle_count"),
        )
        .group_by(Vehicle.owner_id)
        .subquery()
    )

    # Main query: all non-admin users + left-join aggregates in one DB round-trip
    total = db.query(User).filter(User.role != UserRole.ADMIN).count()
    offset = (page - 1) * per_page
    rows = (
        db.query(
            User,
            last_pay_sq.c.last_payment_amount,
            last_pay_sq.c.last_payment_date,
            func.coalesce(vcount_sq.c.vehicle_count, 0).label("vehicle_count"),
        )
        .filter(User.role != UserRole.ADMIN)
        .outerjoin(last_pay_sq, User.id == last_pay_sq.c.user_id)
        .outerjoin(vcount_sq, User.id == vcount_sq.c.owner_id)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    results = []
    for u, last_pay_amount, last_pay_date, v_count in rows:
        is_active = bool(u.subscription_expires and u.subscription_expires > now)
        results.append({
            "id":                   u.id,
            "full_name":            u.full_name,
            "email":                u.email,
            "role":                 u.role,
            "subscription_tier":    u.subscription_tier,
            "subscription_expires": u.subscription_expires.isoformat() if u.subscription_expires else None,
            "is_active":            is_active,
            "last_payment_amount":  float(last_pay_amount) if last_pay_amount is not None else None,
            "last_payment_date":    last_pay_date.isoformat() if last_pay_date else None,
            "vehicle_count":        int(v_count),
        })

    return {"total": total, "page": page, "per_page": per_page, "users": results}


# Vehicles: All Listings

@router.get("/vehicles/all")
def admin_list_all_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: list ALL vehicles across every status. Auto-purges expired admin listings."""
    _purge_expired_admin_listings(db)

    total = db.query(Vehicle).count()
    offset = (page - 1) * per_page
    vehicles = (
        db.query(Vehicle)
        .order_by(Vehicle.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )
    owner_cache = {}
    def _owner(oid):
        if oid not in owner_cache:
            owner_cache[oid] = db.query(User).filter(User.id == oid).first()
        return owner_cache[oid]

    return VehicleListResponse(
        total=total, page=page, per_page=per_page,
        vehicles=[_vehicle_response(v, _owner(v.owner_id)) for v in vehicles]
    )


# Vehicles: Pending

@router.get("/vehicles/pending", response_model=VehicleListResponse)
def get_pending_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: pending vehicles awaiting approval."""
    _purge_expired_admin_listings(db)

    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING)
    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()

    owner_cache = {}
    def _owner(oid):
        if oid not in owner_cache:
            owner_cache[oid] = db.query(User).filter(User.id == oid).first()
        return owner_cache[oid]

    return VehicleListResponse(
        total=total, page=page, per_page=per_page,
        vehicles=[_vehicle_response(v, _owner(v.owner_id)) for v in vehicles]
    )


# Vehicles: Approve / Reject / Edit / Delete

@router.put("/vehicles/{vehicle_id}/approve", response_model=VehicleResponse)
def approve_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status not in (VehicleStatus.PENDING, VehicleStatus.REJECTED):
        raise HTTPException(status_code=400, detail=f"Cannot approve a vehicle with status '{vehicle.status}'")
    vehicle.status = VehicleStatus.ACTIVE
    db.commit()
    db.refresh(vehicle)
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    return _vehicle_response(vehicle, owner)


@router.put("/vehicles/{vehicle_id}/reject", response_model=VehicleResponse)
def reject_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status != VehicleStatus.PENDING:
        raise HTTPException(status_code=400, detail="Vehicle is not pending")
    vehicle.status = VehicleStatus.REJECTED
    db.commit()
    db.refresh(vehicle)
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    return _vehicle_response(vehicle, owner)


@router.put("/vehicles/{vehicle_id}/edit", response_model=VehicleResponse)
def admin_edit_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: edit any vehicle listing (useful for fixing errors before approving)."""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    return _vehicle_response(vehicle, owner)


@router.delete("/vehicles/{vehicle_id}")
def admin_delete_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted"}
