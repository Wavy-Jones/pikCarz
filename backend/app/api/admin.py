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
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def _seller_name(vehicle, owner) -> str:
    if vehicle.contact_name:
        return vehicle.contact_name
    if owner:
        return owner.business_name or owner.full_name
    return "Unknown"


def _vehicle_response(vehicle, owner) -> VehicleResponse:
    resp = VehicleResponse.model_validate(vehicle)
    resp.seller_name   = _seller_name(vehicle, owner)
    resp.seller_type   = owner.role if owner else "individual"
    resp.is_verified   = bool(owner.is_verified_dealer) if owner and owner.role == "dealer" else False
    resp.contact_name  = vehicle.contact_name or None
    resp.contact_phone = vehicle.contact_phone or None
    return resp


def _purge_expired_admin_listings(db: Session):
    now = datetime.utcnow()
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
    return {
        "total_users":      db.query(User).count(),
        "total_vehicles":   db.query(Vehicle).count(),
        "active_vehicles":  db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count(),
        "pending_vehicles": db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING).count(),
        "total_dealers":    db.query(User).filter(User.role == UserRole.DEALER).count(),
        "verified_dealers": db.query(User).filter(
            User.role == UserRole.DEALER, User.is_verified_dealer == True
        ).count(),
    }


@router.get("/subscriptions")
def admin_get_subscriptions(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Raw SQL with explicit ::text casts on all ENUM columns.
    PostgreSQL raises 'operator does not exist: userrole != unknown' when you
    compare an ENUM column directly to a string literal without casting.
    """
    try:
        now = datetime.utcnow()
        offset = (page - 1) * per_page

        # role is a PostgreSQL ENUM — cast to ::text before comparing with string
        count_row = db.execute(
            text("SELECT COUNT(*) FROM users WHERE role::text != 'admin'")
        ).fetchone()
        total = int(count_row[0]) if count_row else 0

        user_rows = db.execute(
            text(
                "SELECT id, full_name, email, role::text, "
                "       subscription_tier::text, subscription_expires "
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

        # Build :id0, :id1 … placeholders (SQLAlchemy text() doesn't support lists)
        id_params = {f"p{i}": uid for i, uid in enumerate(user_ids)}
        in_clause = ", ".join(f":p{i}" for i in range(len(user_ids)))

        # status is also a PostgreSQL ENUM — cast ::text
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
            uid, full_name, email, role, sub_tier, sub_expires = row
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
            })

        return {"total": total, "page": page, "per_page": per_page, "users": results}

    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"[/api/admin/subscriptions] 500 ERROR:\n{tb}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__, "trace": tb},
        )


@router.get("/vehicles/all")
def admin_list_all_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _purge_expired_admin_listings(db)
    total  = db.query(func.count(Vehicle.id)).scalar() or 0
    offset = (page - 1) * per_page
    vehicles = (
        db.query(Vehicle)
        .order_by(Vehicle.created_at.desc())
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
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _purge_expired_admin_listings(db)
    query  = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING)
    total  = query.count()
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
    return _vehicle_response(v, db.query(User).filter(User.id == v.owner_id).first())


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
