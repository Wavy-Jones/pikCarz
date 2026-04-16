"""
Vehicle API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models import VehicleStatus, VehicleCategory, UserRole
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.core.deps import get_current_user
from app.services.cloudinary import upload_multiple_vehicle_images, delete_vehicle_images
from app.config import settings
from datetime import datetime, timedelta
import time
import hashlib

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


def _seller_name(vehicle: Vehicle, owner: User | None) -> str:
    """
    Return the display name for a listing.
    Admin listings on behalf of someone use contact_name.
    Otherwise use the owner's business or full name.
    """
    if vehicle.contact_name:
        return vehicle.contact_name
    if owner:
        return owner.business_name or owner.full_name
    return "Unknown"


def _build_response(vehicle: Vehicle, owner: User | None) -> VehicleResponse:
    """Helper: build a VehicleResponse with correct seller + contact info."""
    resp = VehicleResponse.model_validate(vehicle)
    resp.seller_name  = _seller_name(vehicle, owner)
    resp.seller_type  = owner.role if owner else "individual"
    resp.is_verified  = bool(owner.is_verified_dealer) if owner and owner.role == "dealer" else False
    resp.contact_name  = vehicle.contact_name  or None
    resp.contact_phone = vehicle.contact_phone or None
    return resp


# ── Public Stats ─────────────────────────────────────────────────────────────

@router.get("/public-stats")
def get_public_stats(db: Session = Depends(get_db)):
    """
    Public statistics for the About page — no auth required.
    Returns live counts from the database.
    """
    active_vehicles = db.query(Vehicle).filter(
        Vehicle.status == VehicleStatus.ACTIVE
    ).count()
    total_vehicles_ever = db.query(Vehicle).count()
    verified_dealers = db.query(User).filter(
        User.role == UserRole.DEALER,
        User.is_verified_dealer == True
    ).count()
    total_dealers = db.query(User).filter(User.role == UserRole.DEALER).count()
    total_users = db.query(User).count()
    return {
        "active_listings": active_vehicles,
        "total_listings": total_vehicles_ever,
        "verified_dealers": verified_dealers,
        "total_dealers": total_dealers,
        "total_users": total_users,
        "provinces_covered": 9,
    }


# ── Upload Signature ──────────────────────────────────────────────────────────

@router.post("/upload-signature")
def get_upload_signature(current_user: User = Depends(get_current_user)):
    """
    Return a signed Cloudinary upload signature so the browser can
    upload images directly to Cloudinary without proxying through Vercel.
    """
    timestamp = int(time.time())
    folder = "pikcarz/vehicles"
    params_to_sign = f"folder={folder}&timestamp={timestamp}"
    signature = hashlib.sha1(
        f"{params_to_sign}{settings.CLOUDINARY_API_SECRET}".encode("utf-8")
    ).hexdigest()
    return {
        "timestamp": timestamp,
        "signature": signature,
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "api_key": settings.CLOUDINARY_API_KEY,
        "folder": folder,
    }


# ── Create Vehicle ────────────────────────────────────────────────────────────

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vehicle listing."""
    # Admin listings on behalf of someone expire after 6 months.
    # All other listings expire after 30 days.
    is_admin_listing = (current_user.role == UserRole.ADMIN)
    expiry_days = 180 if is_admin_listing else 30

    new_vehicle = Vehicle(
        owner_id=current_user.id,
        make=vehicle_data.make,
        model=vehicle_data.model,
        year=vehicle_data.year,
        category=VehicleCategory(vehicle_data.category),
        price=vehicle_data.price,
        mileage=vehicle_data.mileage,
        transmission=vehicle_data.transmission,
        fuel_type=vehicle_data.fuel_type,
        color=vehicle_data.color,
        title=vehicle_data.title,
        description=vehicle_data.description,
        province=vehicle_data.province,
        city=vehicle_data.city,
        images=vehicle_data.images or [],
        contact_name=vehicle_data.contact_name or None,
        contact_phone=vehicle_data.contact_phone or None,
        status=VehicleStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=expiry_days),
    )

    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    return _build_response(new_vehicle, current_user)


# ── List Vehicles (public) ────────────────────────────────────────────────────

@router.get("/", response_model=VehicleListResponse)
def list_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    make: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    province: Optional[str] = None,
    status: str = "active",
    db: Session = Depends(get_db)
):
    """List all vehicles with filters and pagination. Expired listings are excluded."""
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus(status))

    # Exclude listings past their expiry date
    now = datetime.utcnow()
    query = query.filter(
        (Vehicle.expires_at == None) | (Vehicle.expires_at > now)
    )

    if category:
        query = query.filter(Vehicle.category == VehicleCategory(category))
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if min_price:
        query = query.filter(Vehicle.price >= min_price)
    if max_price:
        query = query.filter(Vehicle.price <= max_price)
    if province:
        query = query.filter(Vehicle.province.ilike(f"%{province}%"))

    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()

    vehicle_responses = []
    for vehicle in vehicles:
        owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        vehicle_responses.append(_build_response(vehicle, owner))

    return VehicleListResponse(total=total, page=page, per_page=per_page, vehicles=vehicle_responses)


# ── Image Upload / Delete ─────────────────────────────────────────────────────

@router.post("/{vehicle_id}/images", response_model=VehicleResponse)
async def upload_vehicle_images(
    vehicle_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    image_urls = await upload_multiple_vehicle_images(files, vehicle_id)
    vehicle.images = (vehicle.images or []) + image_urls
    db.commit()
    db.refresh(vehicle)
    return _build_response(vehicle, current_user)


@router.delete("/{vehicle_id}/images/{image_index}", response_model=VehicleResponse)
def delete_vehicle_image(
    vehicle_id: int,
    image_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if not vehicle.images or image_index >= len(vehicle.images):
        raise HTTPException(status_code=404, detail="Image not found")
    delete_vehicle_images([vehicle.images[image_index]])
    vehicle.images.pop(image_index)
    db.commit()
    db.refresh(vehicle)
    return _build_response(vehicle, current_user)


# ── Get / Update / Delete Single Vehicle ─────────────────────────────────────

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    return _build_response(vehicle, owner)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in vehicle_data.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return _build_response(vehicle, current_user)


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(vehicle)
    db.commit()


# ── My Listings ───────────────────────────────────────────────────────────────

@router.get("/my/listings", response_model=VehicleListResponse)
def get_my_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vehicles owned by current user (including admin-on-behalf listings)."""
    query = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id)
    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    return VehicleListResponse(
        total=total, page=page, per_page=per_page,
        vehicles=[_build_response(v, current_user) for v in vehicles]
    )
