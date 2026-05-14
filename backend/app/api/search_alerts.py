"""
Search Alerts API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.search_alert import SearchAlert
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/search-alerts", tags=["Search Alerts"])


class AlertCreate(BaseModel):
    make:      Optional[str]   = None
    category:  Optional[str]   = None
    province:  Optional[str]   = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None


@router.get("/")
def list_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alerts = db.query(SearchAlert).filter(SearchAlert.user_id == current_user.id).all()
    return [
        {
            "id":        a.id,
            "make":      a.make,
            "category":  a.category,
            "province":  a.province,
            "min_price": float(a.min_price) if a.min_price else None,
            "max_price": float(a.max_price) if a.max_price else None,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.post("/")
def create_alert(data: AlertCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not any([data.make, data.category, data.province, data.min_price, data.max_price]):
        raise HTTPException(status_code=400, detail="At least one filter is required.")
    existing = db.query(SearchAlert).filter(SearchAlert.user_id == current_user.id).count()
    if existing >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 search alerts allowed.")
    alert = SearchAlert(
        user_id=current_user.id,
        make=data.make,
        category=data.category,
        province=data.province,
        min_price=data.min_price,
        max_price=data.max_price,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "created": True}


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    alert = db.query(SearchAlert).filter(
        SearchAlert.id == alert_id,
        SearchAlert.user_id == current_user.id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"deleted": True}
