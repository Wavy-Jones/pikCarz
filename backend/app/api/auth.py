"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models import UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.services.email import send_password_reset_email, send_welcome_email
import secrets

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (individual or dealer)"""
    
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=UserRole.DEALER if user_data.role == "dealer" else UserRole.INDIVIDUAL,
        business_name=user_data.business_name,
        business_registration=user_data.business_registration,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send welcome email (non-blocking, don't fail registration if email fails)
    try:
        send_welcome_email(
            to_email=new_user.email,
            user_name=new_user.full_name
        )
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
    
    # Create token — sub MUST be a string per JWT spec (RFC 7519)
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password"""
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    
    # Create token — sub MUST be a string per JWT spec (RFC 7519)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.post("/request-password-reset")
def request_password_reset(request_data: dict, db: Session = Depends(get_db)):
    """Request password reset - generates reset token and stores in database"""
    
    email = request_data.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Find user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If the email exists, reset instructions have been sent"}
    
    # Generate reset token (valid for 1 hour)
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    # Store token in database
    try:
        # Invalidate any existing tokens for this user
        db.execute(
            text("UPDATE password_reset_tokens SET used = TRUE WHERE user_id = :user_id AND used = FALSE"),
            {"user_id": user.id}
        )
        
        # Create new reset token
        db.execute(
            text("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at, used)
                VALUES (:user_id, :token, :expires_at, FALSE)
            """),
            {
                "user_id": user.id,
                "token": reset_token,
                "expires_at": expires_at
            }
        )
        
        db.commit()
        
        # Generate reset link
        reset_link = f"https://pikcarz.co.za/reset-password.html?token={reset_token}"
        
        # Send password reset email
        email_sent = send_password_reset_email(
            to_email=user.email,
            reset_link=reset_link,
            user_name=user.full_name
        )
        
        # Return response (don't reveal if email exists)
        return {
            "message": "If the email exists, reset instructions have been sent"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error creating reset token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create reset token")

@router.post("/reset-password")
def reset_password(request_data: dict, db: Session = Depends(get_db)):
    """Reset password using token"""
    
    token = request_data.get("token")
    new_password = request_data.get("new_password")
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")
    
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    try:
        # Find valid token
        result = db.execute(
            text("""
                SELECT user_id, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = :token
            """),
            {"token": token}
        ).fetchone()
        
        if not result:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        user_id, expires_at, used = result
        
        # Check if token is used
        if used:
            raise HTTPException(status_code=400, detail="This reset link has already been used")
        
        # Check if token is expired
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=400, detail="This reset link has expired")
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Mark token as used
        db.execute(
            text("UPDATE password_reset_tokens SET used = TRUE WHERE token = :token"),
            {"token": token}
        )
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET SUCCESSFUL")
        print(f"{'='*60}")
        print(f"Email: {user.email}")
        print(f"User: {user.full_name}")
        print(f"{'='*60}\n")
        
        return {
            "message": "Password reset successful! You can now sign in with your new password.",
            "email": user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error resetting password: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset password")
