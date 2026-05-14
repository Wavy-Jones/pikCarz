"""
Favourites API — save/unsave listings
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.favourite import Favourite
from app.core.deps import get_current_user
from app.models import VehicleStatus

router = APIRouter(prefix="/api/favourites", tags=["Favourites"])


@router.get("/")
def list_favourites(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = db.query(Favourite).filter(Favourite.user_id == current_user.id).all()
    result = []
    for fav in favs:
        v = fav.vehicle
        if v and v.status == VehicleStatus.ACTIVE:
            result.append({
                "favourite_id": fav.id,
                "vehicle_id":   v.id,
                "title":        v.title,
                "make":         v.make,
                "model":        v.model,
                "year":         v.year,
                "price":        float(v.price),
                "province":     v.province,
                "city":         v.city,
                "images":       v.images or [],
                "saved_at":     fav.created_at.isoformat(),
            })
    return result


@router.post("/{vehicle_id}")
def save_favourite(vehicle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    try:
        fav = Favourite(user_id=current_user.id, vehicle_id=vehicle_id)
        db.add(fav)
        db.commit()
        return {"saved": True, "vehicle_id": vehicle_id}
    except IntegrityError:
        db.rollback()
        return {"saved": True, "vehicle_id": vehicle_id}


@router.delete("/{vehicle_id}")
def remove_favourite(vehicle_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favourite).filter(
        Favourite.user_id == current_user.id,
        Favourite.vehicle_id == vehicle_id
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"saved": False, "vehicle_id": vehicle_id}


@router.get("/ids")
def get_favourite_ids(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    favs = db.query(Favourite.vehicle_id).filter(Favourite.user_id == current_user.id).all()
    return [f.vehicle_id for f in favs]
