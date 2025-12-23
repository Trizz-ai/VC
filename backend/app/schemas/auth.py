"""
Authentication schemas for request/response models
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserRegister(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    consent_granted: bool = False


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    consent_granted: bool
    consent_timestamp: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., min_length=8, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class SessionToken(BaseModel):
    """Session token response schema"""
    session_token: str
    expires_in: int


class PublicToken(BaseModel):
    """Public token response schema"""
    public_token: str
    expires_in: int
    share_url: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str