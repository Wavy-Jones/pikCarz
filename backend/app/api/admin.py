"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models import VehicleStatus
from app.schemas.vehicle import VehicleResponse, VehicleListResponse
from app.core.deps import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/vehicles/pending", response_model=VehicleListResponse)
def get_pending_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending vehicle listings (admin only)"""
    
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING)
    
    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    
    # Add seller info
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

@router.put("/vehicles/{vehicle_id}/approve", response_model=VehicleResponse)
def approve_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a pending vehicle listing (admin only)"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.status = VehicleStatus.ACTIVE
    db.commit()
    db.refresh(vehicle)
    
    # Add seller info
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
    response.seller_type = owner.role if owner else "individual"
    response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
    
    return response

@router.put("/vehicles/{vehicle_id}/reject", response_model=VehicleResponse)
def reject_vehicle(
    vehicle_id: int,
    reason: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a pending vehicle listing (admin only)"""
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.status = VehicleStatus.REJECTED
    db.commit()
    db.refresh(vehicle)
    
    # TODO: Send email notification to owner about rejection
    
    # Add seller info
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
    response.seller_type = owner.role if owner else "individual"
    response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
    
    return response

@router.get("/users", response_model=dict)
def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    role: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    offset = (page - 1) * per_page
    users = query.order_by(User.created_at.desc()).offset(offset).limit(per_page).all()
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "subscription_tier": u.subscription_tier,
                "is_active": u.is_active,
                "created_at": u.created_at
            } for u in users
        ]
    }

@router.put("/users/{user_id}/verify-dealer")
def verify_dealer(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Verify a dealer (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "dealer":
        raise HTTPException(status_code=400, detail="User is not a dealer")
    
    user.is_verified_dealer = True
    db.commit()
    
    return {"status": "success", "message": f"Dealer {user.business_name or user.full_name} verified"}

@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (admin only)"""
    
    total_users = db.query(User).count()
    total_dealers = db.query(User).filter(User.role == "dealer").count()
    total_vehicles = db.query(Vehicle).count()
    pending_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count()
    
    return {
        "total_users": total_users,
        "total_dealers": total_dealers,
        "total_vehicles": total_vehicles,
        "pending_vehicles": pending_vehicles,
        "active_vehicles": active_vehicles
    }
