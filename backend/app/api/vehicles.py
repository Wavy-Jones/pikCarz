"""
Vehicle API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models import VehicleStatus, VehicleCategory
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.core.deps import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vehicle listing"""
    
    # Create vehicle
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
        status=VehicleStatus.PENDING,  # Admin approval required
        expires_at=datetime.utcnow() + timedelta(days=30)  # 30-day listing
    )
    
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    
    # Add seller info to response
    response = VehicleResponse.model_validate(new_vehicle)
    response.seller_name = current_user.business_name or current_user.full_name
    response.seller_type = current_user.role
    response.is_verified = current_user.is_verified_dealer if current_user.role == "dealer" else False
    
    return response

@router.get("/", response_model=VehicleListResponse)
def list_vehicles(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = None,
    make: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    province: Optional[str] = None,
    status: str = "active",  # Only show active by default
    db: Session = Depends(get_db)
):
    """List all vehicles with filters and pagination"""
    
    # Build query
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus(status))
    
    # Apply filters
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
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Add seller info to each vehicle
    vehicle_responses = []
    for vehicle in vehicles:
        owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        response = VehicleResponse.model_validate(vehicle)
        response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
        response.seller_type = owner.role if owner else "individual"
        response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
        vehicle_responses.append(response)
    
    return VehicleListResponse(
        total=total,
        page=page,
        per_page=per_page,
        vehicles=vehicle_responses
    )

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    """Get a specific vehicle by ID"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Add seller info
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
    response.seller_type = owner.role if owner else "individual"
    response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
    
    return response

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a vehicle listing (owner only)"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check ownership
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this vehicle")
    
    # Update fields
    update_data = vehicle_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    # Add seller info
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = current_user.business_name or current_user.full_name
    response.seller_type = current_user.role
    response.is_verified = current_user.is_verified_dealer if current_user.role == "dealer" else False
    
    return response

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vehicle listing (owner only)"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Check ownership
    if vehicle.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this vehicle")
    
    db.delete(vehicle)
    db.commit()
    
    return None

@router.get("/my/listings", response_model=VehicleListResponse)
def get_my_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vehicles owned by current user"""
    
    query = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id)
    
    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Add seller info
    vehicle_responses = []
    for vehicle in vehicles:
        response = VehicleResponse.model_validate(vehicle)
        response.seller_name = current_user.business_name or current_user.full_name
        response.seller_type = current_user.role
        response.is_verified = current_user.is_verified_dealer if current_user.role == "dealer" else False
        vehicle_responses.append(response)
    
    return VehicleListResponse(
        total=total,
        page=page,
        per_page=per_page,
        vehicles=vehicle_responses
    )
