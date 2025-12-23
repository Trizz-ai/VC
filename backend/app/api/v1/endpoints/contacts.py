"""
Contact management endpoints
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user_dependency
from app.core.database import get_db
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate
from app.services.contact_service import ContactService

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact"""
    try:
        contact_service = ContactService(db)
        contact = await contact_service.create_contact(contact_data)
        return ContactResponse.from_orm(contact)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create contact: {str(e)}"
        )


# IMPORTANT: Specific routes must come BEFORE parameterized routes
@router.get("/me", response_model=ContactResponse)
async def get_current_user_profile(
    current_user: Contact = Depends(get_current_user_dependency)
):
    """Get current user's profile"""
    return ContactResponse.from_orm(current_user)


@router.put("/me", response_model=ContactResponse)
async def update_current_user_profile(
    contact_data: ContactUpdate,
    current_user: Contact = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    try:
        contact_service = ContactService(db)
        # Contact.id is a string, pass ContactUpdate directly
        contact = await contact_service.update_contact(str(current_user.id), contact_data)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        return ContactResponse.from_orm(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


# Now parameterized routes can be defined
@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get contact by ID"""
    try:
        contact_service = ContactService(db)
        # Contact.id is a string
        contact = await contact_service.get_contact_by_id(str(contact_id))
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        return ContactResponse.from_orm(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contact: {str(e)}"
        )


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update contact"""
    try:
        contact_service = ContactService(db)
        # Contact.id is a string
        contact = await contact_service.update_contact(str(contact_id), contact_data)
        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found"
            )
        return ContactResponse.from_orm(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update contact: {str(e)}"
        )


@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List contacts with pagination"""
    try:
        contact_service = ContactService(db)
        contacts = await contact_service.list_contacts(skip=skip, limit=limit)
        return [ContactResponse.from_orm(contact) for contact in contacts]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list contacts: {str(e)}"
        )
