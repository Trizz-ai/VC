"""
Contact service for business logic
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    """Service class for contact operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_contact(self, contact_data: ContactCreate) -> Contact:
        """Create a new contact"""
        contact = Contact(
            email=contact_data.email,
            phone=contact_data.phone,
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            notes=contact_data.notes,
            consent_granted=contact_data.consent_granted,
        )
        
        if contact_data.consent_granted:
            contact.grant_consent()
        
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def get_contact_by_id(self, contact_id) -> Optional[Contact]:
        """Get contact by ID"""
        # Contact.id is a String, not UUID
        result = await self.db.execute(
            select(Contact).where(Contact.id == str(contact_id))
        )
        return result.scalar_one_or_none()
    
    async def get_contact_by_email(self, email: str) -> Optional[Contact]:
        """Get contact by email"""
        result = await self.db.execute(
            select(Contact).where(Contact.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_contact(self, contact_id, contact_data: ContactUpdate) -> Optional[Contact]:
        """Update contact"""
        # Contact.id is a String, not UUID
        contact = await self.get_contact_by_id(str(contact_id))
        if not contact:
            return None
        
        update_data = contact_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        if contact_data.consent_granted is not None:
            if contact_data.consent_granted:
                contact.grant_consent()
            else:
                contact.revoke_consent()
        
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def list_contacts(self, skip: int = 0, limit: int = 100) -> List[Contact]:
        """List contacts with pagination"""
        result = await self.db.execute(
            select(Contact)
            .offset(skip)
            .limit(limit)
            .order_by(Contact.created_at.desc())
        )
        return result.scalars().all()
    
    async def delete_contact(self, contact_id) -> bool:
        """Delete contact"""
        # Contact.id is a String, not UUID
        contact = await self.get_contact_by_id(str(contact_id))
        if not contact:
            return False
        
        await self.db.delete(contact)
        await self.db.commit()
        return True
