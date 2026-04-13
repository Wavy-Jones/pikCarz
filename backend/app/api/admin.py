"""
Admin API routes - Approve/reject vehicles, manage users
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models import VehicleStatus, UserRole
from app.schemas.vehicle import VehicleResponse, VehicleListResponse
from app.core.deps import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/vehicles/all")
def admin_list_all_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: list ALL vehicles across every status"""
    total = db.query(Vehicle).count()
    offset = (page - 1) * per_page
    vehicles = db.query(Vehicle).order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    vehicle_responses = []
    for vehicle in vehicles:
        owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        response = VehicleResponse.model_validate(vehicle)
        response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
        response.seller_type = owner.role if owner else "individual"
        response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
        vehicle_responses.append(response)
    return VehicleListResponse(total=total, page=page, per_page=per_page, vehicles=vehicle_responses)


@router.delete("/vehicles/{vehicle_id}")
def admin_delete_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: delete any vehicle listing regardless of status or owner"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted"}


@router.get("/vehicles/pending", response_model=VehicleListResponse)
def get_pending_vehicles(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending vehicles awaiting approval (Admin only)"""
    query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING)
    total = query.count()
    offset = (page - 1) * per_page
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(offset).limit(per_page).all()
    vehicle_responses = []
    for vehicle in vehicles:
        owner = db.query(User).filter(User.id == vehicle.owner_id).first()
        response = VehicleResponse.model_validate(vehicle)
        response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
        response.seller_type = owner.role if owner else "individual"
        response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
        vehicle_responses.append(response)
    return VehicleListResponse(total=total, page=page, per_page=per_page, vehicles=vehicle_responses)


@router.put("/vehicles/{vehicle_id}/approve", response_model=VehicleResponse)
def approve_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a pending vehicle listing (Admin only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status != VehicleStatus.PENDING:
        raise HTTPException(status_code=400, detail="Vehicle is not in pending status")
    vehicle.status = VehicleStatus.ACTIVE
    db.commit()
    db.refresh(vehicle)
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
    response.seller_type = owner.role if owner else "individual"
    response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
    return response


@router.put("/vehicles/{vehicle_id}/reject", response_model=VehicleResponse)
def reject_vehicle(
    vehicle_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a pending vehicle listing (Admin only)"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.status != VehicleStatus.PENDING:
        raise HTTPException(status_code=400, detail="Vehicle is not in pending status")
    vehicle.status = VehicleStatus.REJECTED
    db.commit()
    db.refresh(vehicle)
    owner = db.query(User).filter(User.id == vehicle.owner_id).first()
    response = VehicleResponse.model_validate(vehicle)
    response.seller_name = owner.business_name or owner.full_name if owner else "Unknown"
    response.seller_type = owner.role if owner else "individual"
    response.is_verified = owner.is_verified_dealer if owner and owner.role == "dealer" else False
    return response


@router.get("/stats")
def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics (Admin only)"""
    total_users = db.query(User).count()
    total_vehicles = db.query(Vehicle).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE).count()
    pending_vehicles = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.PENDING).count()
    total_dealers = db.query(User).filter(User.role == UserRole.DEALER).count()
    verified_dealers = db.query(User).filter(
        User.role == UserRole.DEALER,
        User.is_verified_dealer == True
    ).count()
    return {
        "total_users": total_users,
        "total_vehicles": total_vehicles,
        "active_vehicles": active_vehicles,
        "pending_vehicles": pending_vehicles,
        "total_dealers": total_dealers,
        "verified_dealers": verified_dealers
    }
