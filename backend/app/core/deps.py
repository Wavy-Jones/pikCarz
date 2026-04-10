"""
FastAPI dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the currently authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # sub is stored as a string (JWT spec) but may be an int in older tokens
    # safely coerce to int either way
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user

def get_current_active_dealer(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is a dealer"""
    if current_user.role != "dealer":
        raise HTTPException(status_code=403, detail="Not authorized - dealer access required")
    return current_user

def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin — accepts role=admin OR is_superuser=True"""
    from app.models import UserRole
    is_admin = (current_user.role == UserRole.ADMIN) or current_user.is_superuser
    if not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized - admin access required")
    return current_user
