"""
Authentication endpoints
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import (
    authenticate_user,
    blacklist_token,
    create_token_pair,
    create_session_token,
    create_public_token,
    get_current_user,
    is_token_blacklisted,
    verify_token,
    TokenType,
)
from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.auth import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    SessionToken,
    PublicToken,
    RefreshTokenRequest,
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Contact:
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_current_user(token, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if user already exists
    from sqlalchemy import select
    result = await db.execute(
        select(Contact).where(Contact.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = Contact(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        consent_granted=user_data.consent_granted,
    )
    
    # Set password
    user.set_password(user_data.password)
    
    # Grant consent if requested
    if user_data.consent_granted:
        user.grant_consent()
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return tokens"""
    user = await authenticate_user(user_credentials.email, user_credentials.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token pair
    token_data = create_token_pair(str(user.id))
    
    return Token(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
        expires_in=15 * 60,  # 15 minutes
    )


@router.post("/logout")
async def logout_user(
    current_user: Contact = Depends(get_current_user_dependency),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and blacklist token"""
    token = credentials.credentials
    success = await blacklist_token(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Contact = Depends(get_current_user_dependency)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not current_user.check_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Set new password
    current_user.set_password(password_data.new_password)
    
    await db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/session-token", response_model=SessionToken)
async def create_session_token_endpoint(
    current_user: Contact = Depends(get_current_user_dependency)
):
    """Create session token for active sessions"""
    session_token = create_session_token(data={"sub": str(current_user.id)})
    
    return SessionToken(
        session_token=session_token,
        expires_in=15 * 60,  # 15 minutes
    )


@router.post("/public-token", response_model=PublicToken)
async def create_public_token_endpoint(
    current_user: Contact = Depends(get_current_user_dependency)
):
    """Create public token for sharing"""
    public_token = create_public_token(data={"sub": str(current_user.id)})
    
    return PublicToken(
        public_token=public_token,
        expires_in=30 * 24 * 60 * 60,  # 30 days
        share_url=f"/public/{public_token}",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    refresh_token = refresh_token_data.refresh_token
    
    # Verify refresh token
    payload = verify_token(refresh_token, TokenType.REFRESH)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if refresh token is blacklisted
    if await is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new token pair
    token_data = create_token_pair(user_id)
    
    # Blacklist old refresh token
    await blacklist_token(refresh_token)
    
    return Token(
        access_token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_type=token_data["token_type"],
        expires_in=15 * 60,  # 15 minutes
    )


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset"""
    from sqlalchemy import select
    from app.services.email_service import EmailService
    
    # Check if user exists
    result = await db.execute(
        select(Contact).where(Contact.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if user exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Create password reset token
    reset_token = create_session_token(
        data={"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # Store reset token in database (you might want to create a separate table for this)
    # For now, we'll use Redis
    from app.core.database import get_redis
    redis_client = await get_redis()
    await redis_client.setex(
        f"password_reset:{reset_token}",
        3600,  # 1 hour
        str(user.id)
    )
    
    # Send email (implement email service)
    email_service = EmailService()
    await email_service.send_password_reset_email(
        email=user.email,
        reset_token=reset_token,
        user_name=user.first_name or "User"
    )
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset"""
    from sqlalchemy import select
    from app.core.database import get_redis
    
    # Verify reset token
    redis_client = await get_redis()
    user_id = await redis_client.get(f"password_reset:{request.token}")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    result = await db.execute(
        select(Contact).where(Contact.id == UUID(user_id.decode()))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.set_password(request.new_password)
    await db.commit()
    
    # Remove reset token
    await redis_client.delete(f"password_reset:{request.token}")
    
    return {"message": "Password reset successfully"}