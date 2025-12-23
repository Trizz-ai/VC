"""
Biometric API endpoints for facial recognition.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.contact import Contact
from app.services.biometric_service import BiometricService

router = APIRouter()


class FaceEnrollmentRequest(BaseModel):
    """Request model for face enrollment."""
    face_image_base64: str = Field(..., description="Base64 encoded face image")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class FaceVerificationRequest(BaseModel):
    """Request model for face verification."""
    face_image_base64: str = Field(..., description="Base64 encoded face image")
    biometric_id: Optional[str] = Field(None, description="Optional specific biometric ID")


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_face(
    request: FaceEnrollmentRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll user's face for biometric verification.
    
    - **face_image_base64**: Base64 encoded face image (JPEG/PNG)
    - **metadata**: Optional metadata about the enrollment
    
    Returns enrolled biometric ID and status.
    """
    biometric_service = BiometricService(db)
    
    result = await biometric_service.enroll_face(
        user_id=str(current_user.id),
        face_image_base64=request.face_image_base64,
        metadata=request.metadata
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Face enrollment failed")
        )
    
    return result


@router.post("/verify")
async def verify_face(
    request: FaceVerificationRequest,
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify user's face against enrolled biometric data.
    
    - **face_image_base64**: Base64 encoded face image (JPEG/PNG)
    - **biometric_id**: Optional specific biometric ID to verify against
    
    Returns verification status and confidence score.
    """
    biometric_service = BiometricService(db)
    
    result = await biometric_service.verify_face(
        user_id=str(current_user.id),
        face_image_base64=request.face_image_base64,
        biometric_id=request.biometric_id
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Face verification failed")
        )
    
    return result


@router.get("/status")
async def get_biometric_status(
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get biometric enrollment status for current user.
    
    Returns enrollment status and biometric details.
    """
    biometric_service = BiometricService(db)
    
    result = await biometric_service.get_biometric_status(
        user_id=str(current_user.id)
    )
    
    return result


@router.delete("/data")
async def delete_biometric_data(
    current_user: Contact = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete all biometric data for current user.
    
    This action is irreversible and will require re-enrollment.
    """
    biometric_service = BiometricService(db)
    
    result = await biometric_service.delete_biometric_data(
        user_id=str(current_user.id)
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Failed to delete biometric data")
        )
    
    return result

