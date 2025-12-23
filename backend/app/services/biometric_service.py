"""
Biometric Service for facial recognition enrollment and verification.

This service handles:
- Face enrollment with image processing
- Face verification during check-in/check-out
- Biometric data storage and retrieval
"""

from typing import Optional, Dict, Any
import base64
import io
from datetime import datetime
from PIL import Image
import hashlib

from sqlalchemy.orm import Session
from app.core.config import settings


class BiometricService:
    """Service for handling biometric operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def enroll_face(
        self,
        user_id: str,
        face_image_base64: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enroll a user's face for biometric verification.
        
        Args:
            user_id: The user's unique identifier
            face_image_base64: Base64 encoded face image
            metadata: Optional metadata about the enrollment
            
        Returns:
            Dict containing enrollment status and biometric_id
        """
        try:
            # Decode and validate image
            image_data = base64.b64decode(face_image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Validate image dimensions and format
            if image.size[0] < 200 or image.size[1] < 200:
                raise ValueError("Image too small. Minimum 200x200 pixels required.")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # In production, this would:
            # 1. Use facial recognition API (AWS Rekognition, Face++, etc.)
            # 2. Extract facial embeddings
            # 3. Store embeddings in database
            # For now, we'll simulate with a hash
            
            # Generate a unique biometric identifier
            biometric_id = hashlib.sha256(
                f"{user_id}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Store biometric data (in production, store embeddings)
            enrollment_data = {
                "biometric_id": biometric_id,
                "user_id": user_id,
                "enrolled_at": datetime.utcnow().isoformat(),
                "status": "active",
                "confidence": 0.95,  # Simulated confidence score
                "metadata": metadata or {}
            }
            
            # In production: Store in biometric_enrollments table
            # For now, return success
            
            return {
                "success": True,
                "biometric_id": biometric_id,
                "message": "Face enrolled successfully",
                "confidence": 0.95
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Face enrollment failed"
            }
    
    async def verify_face(
        self,
        user_id: str,
        face_image_base64: str,
        biometric_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a user's face against their enrolled biometric data.
        
        Args:
            user_id: The user's unique identifier
            face_image_base64: Base64 encoded face image for verification
            biometric_id: Optional specific biometric ID to verify against
            
        Returns:
            Dict containing verification status and confidence score
        """
        try:
            # Decode and validate image
            image_data = base64.b64decode(face_image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Validate image
            if image.size[0] < 200 or image.size[1] < 200:
                raise ValueError("Image too small. Minimum 200x200 pixels required.")
            
            # In production, this would:
            # 1. Retrieve stored facial embeddings for user
            # 2. Extract embeddings from verification image
            # 3. Compare embeddings using facial recognition API
            # 4. Return confidence score
            
            # Simulate face verification
            # In production: Use AWS Rekognition CompareFaces or similar
            
            confidence = 0.92  # Simulated confidence score
            threshold = 0.85   # Minimum confidence threshold
            
            is_verified = confidence >= threshold
            
            return {
                "success": True,
                "verified": is_verified,
                "confidence": confidence,
                "threshold": threshold,
                "user_id": user_id,
                "verified_at": datetime.utcnow().isoformat(),
                "message": "Face verified successfully" if is_verified else "Face verification failed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "verified": False,
                "error": str(e),
                "message": "Face verification failed"
            }
    
    async def get_biometric_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get the biometric enrollment status for a user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dict containing enrollment status
        """
        # In production: Query biometric_enrollments table
        # For now, simulate response
        
        return {
            "user_id": user_id,
            "enrolled": True,  # Simulated
            "biometric_id": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "enrolled_at": datetime.utcnow().isoformat(),
            "status": "active",
            "face_enrolled": True,
            "last_verification": None
        }
    
    async def delete_biometric_data(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all biometric data for a user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Dict containing deletion status
        """
        try:
            # In production: Delete from biometric_enrollments table
            # and remove stored embeddings
            
            return {
                "success": True,
                "message": "Biometric data deleted successfully",
                "user_id": user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete biometric data"
            }


# Integration Notes for Production:
# 
# 1. AWS Rekognition:
#    - boto3.client('rekognition')
#    - IndexFaces for enrollment
#    - CompareFaces for verification
#
# 2. Face++ (Megvii):
#    - REST API integration
#    - Face detection and comparison
#
# 3. Azure Face API:
#    - Azure Cognitive Services
#    - Face detection, verification, identification
#
# 4. Database Schema:
#    CREATE TABLE biometric_enrollments (
#        id UUID PRIMARY KEY,
#        user_id UUID REFERENCES contacts(id),
#        biometric_id VARCHAR(255) UNIQUE,
#        face_embedding BYTEA,  -- Store facial embeddings
#        enrolled_at TIMESTAMP,
#        status VARCHAR(50),
#        metadata JSONB,
#        created_at TIMESTAMP DEFAULT NOW()
#    );



