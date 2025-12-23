"""
Authentication utilities for JWT token management
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db, get_redis
from app.models.contact import Contact

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token types
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"
    SESSION = "session"
    PUBLIC = "public"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    from datetime import timezone
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT exp expects Unix timestamp (seconds since epoch)
    to_encode.update({"exp": int(expire.timestamp()), "type": TokenType.ACCESS})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    from datetime import timezone
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": int(expire.timestamp()), "type": TokenType.REFRESH})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_session_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT session token"""
    from datetime import timezone
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.SESSION_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp()), "type": TokenType.SESSION})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_public_token(data: dict) -> str:
    """Create JWT public token for sharing"""
    from datetime import timezone
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.PUBLIC_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": int(expire.timestamp()), "type": TokenType.PUBLIC})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = TokenType.ACCESS) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            logger.warning("Token missing expiration")
            return None
        
        # Use timezone-aware datetime for comparison
        from datetime import timezone
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        if now > exp_datetime:
            logger.warning(f"Token expired: now={now}, exp={exp_datetime}")
            return None
        
        return payload
    except JWTError as e:
        logger.warning(f"JWT error: {e}")
        return None


async def get_current_user(
    token: str, 
    db: AsyncSession
) -> Optional[Contact]:
    """Get current user from JWT token"""
    payload = verify_token(token, TokenType.ACCESS)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        # Contact.id is a String, not UUID
        result = await db.execute(
            select(Contact).where(Contact.id == str(user_id))
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


async def get_current_user_from_session(
    token: str, 
    db: AsyncSession
) -> Optional[Contact]:
    """Get current user from session token"""
    payload = verify_token(token, TokenType.SESSION)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        # Contact.id is a String, not UUID
        result = await db.execute(
            select(Contact).where(Contact.id == str(user_id))
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error getting current user from session: {e}")
        return None


async def blacklist_token(token: str) -> bool:
    """Add token to blacklist"""
    try:
        redis_client = await get_redis()
        payload = verify_token(token)
        if not payload:
            return False
        
        # Calculate time until expiration
        exp = payload.get("exp")
        if exp:
            expire_time = datetime.fromtimestamp(exp) - datetime.utcnow()
            if expire_time.total_seconds() > 0:
                await redis_client.setex(
                    f"blacklist:{token}",
                    int(expire_time.total_seconds()),
                    "1"
                )
                return True
        return False
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    try:
        redis_client = await get_redis()
        result = await redis_client.get(f"blacklist:{token}")
        return result is not None
    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}")
        return False


async def authenticate_user(
    email: str, 
    password: str, 
    db: AsyncSession
) -> Optional[Contact]:
    """Authenticate user with email and password"""
    try:
        result = await db.execute(
            select(Contact).where(Contact.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None


# Security scheme for JWT Bearer tokens - shared instance
_security_scheme = HTTPBearer()

async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(_security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Contact:
    """Dependency to get current user from JWT token"""
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


def create_token_pair(user_id: str) -> dict:
    """Create access and refresh token pair"""
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
