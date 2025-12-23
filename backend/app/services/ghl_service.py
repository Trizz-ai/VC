"""
GoHighLevel CRM integration service
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.contact import Contact
from app.models.session import Session
from app.models.meeting import Meeting

logger = logging.getLogger(__name__)


class GHLService:
    """Service for GoHighLevel CRM integration"""
    
    def __init__(self):
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.api_key = settings.GHL_API_KEY
        self.location_id = settings.GHL_LOCATION_ID
        self.timeout = 30.0
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make authenticated request to GHL API"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params
                )
                
                if response.status_code in [200, 201, 204]:
                    return response.json() if response.content else {}
                else:
                    logger.error(f"GHL API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making GHL request: {e}")
            return None
    
    async def create_contact(
        self,
        contact: Contact,
        db: AsyncSession
    ) -> Optional[str]:
        """Create contact in GHL"""
        try:
            contact_data = {
                "firstName": contact.first_name or "",
                "lastName": contact.last_name or "",
                "email": contact.email,
                "phone": contact.phone or "",
                "source": "Verified Compliance App",
                "locationId": self.location_id,
                "tags": ["verified-compliance", "attendance-tracking"],
                "customFields": [
                    {
                        "key": "consent_granted",
                        "value": str(contact.consent_granted)
                    },
                    {
                        "key": "consent_timestamp",
                        "value": contact.consent_timestamp.isoformat() if contact.consent_timestamp else ""
                    },
                    {
                        "key": "app_user_id",
                        "value": str(contact.id)
                    }
                ]
            }
            
            result = await self._make_request("POST", "contacts/", data=contact_data)
            
            if result and "contact" in result:
                ghl_contact_id = result["contact"]["id"]
                
                # Update local contact with GHL ID
                contact.ghl_contact_id = ghl_contact_id
                await db.commit()
                
                logger.info(f"Created GHL contact {ghl_contact_id} for user {contact.id}")
                return ghl_contact_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating GHL contact: {e}")
            return None
    
    async def update_contact(
        self,
        contact: Contact,
        db: AsyncSession
    ) -> bool:
        """Update contact in GHL"""
        try:
            if not contact.ghl_contact_id:
                logger.warning(f"No GHL contact ID for user {contact.id}")
                return False
            
            contact_data = {
                "firstName": contact.first_name or "",
                "lastName": contact.last_name or "",
                "email": contact.email,
                "phone": contact.phone or "",
                "customFields": [
                    {
                        "key": "consent_granted",
                        "value": str(contact.consent_granted)
                    },
                    {
                        "key": "consent_timestamp",
                        "value": contact.consent_timestamp.isoformat() if contact.consent_timestamp else ""
                    }
                ]
            }
            
            result = await self._make_request(
                "PUT",
                f"contacts/{contact.ghl_contact_id}",
                data=contact_data
            )
            
            if result:
                logger.info(f"Updated GHL contact {contact.ghl_contact_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating GHL contact: {e}")
            return False
    
    async def create_opportunity(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting,
        db: AsyncSession
    ) -> Optional[str]:
        """Create opportunity for attendance session"""
        try:
            if not contact.ghl_contact_id:
                logger.warning(f"No GHL contact ID for user {contact.id}")
                return None
            
            opportunity_data = {
                "contactId": contact.ghl_contact_id,
                "locationId": self.location_id,
                "name": f"Attendance - {meeting.name}",
                "status": "attended" if session.status.value == "completed" else "in_progress",
                "source": "Verified Compliance App",
                "tags": ["attendance", "verified-compliance", meeting.name.lower().replace(" ", "-")],
                "customFields": [
                    {
                        "key": "session_id",
                        "value": str(session.id)
                    },
                    {
                        "key": "meeting_name",
                        "value": meeting.name
                    },
                    {
                        "key": "check_in_time",
                        "value": session.check_in_time.isoformat() if session.check_in_time else ""
                    },
                    {
                        "key": "check_out_time",
                        "value": session.check_out_time.isoformat() if session.check_out_time else ""
                    },
                    {
                        "key": "session_notes",
                        "value": session.session_notes or ""
                    }
                ]
            }
            
            result = await self._make_request("POST", "opportunities/", data=opportunity_data)
            
            if result and "opportunity" in result:
                opportunity_id = result["opportunity"]["id"]
                logger.info(f"Created GHL opportunity {opportunity_id} for session {session.id}")
                return opportunity_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating GHL opportunity: {e}")
            return None
    
    async def create_task(
        self,
        contact: Contact,
        title: str,
        description: str,
        due_date: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> Optional[str]:
        """Create task for contact"""
        try:
            if not contact.ghl_contact_id:
                logger.warning(f"No GHL contact ID for user {contact.id}")
                return None
            
            task_data = {
                "contactId": contact.ghl_contact_id,
                "locationId": self.location_id,
                "title": title,
                "description": description,
                "status": "pending",
                "dueDate": due_date.isoformat() if due_date else None,
                "tags": ["verified-compliance", "automated"]
            }
            
            result = await self._make_request("POST", "tasks/", data=task_data)
            
            if result and "task" in result:
                task_id = result["task"]["id"]
                logger.info(f"Created GHL task {task_id} for contact {contact.ghl_contact_id}")
                return task_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating GHL task: {e}")
            return None
    
    async def add_contact_tag(
        self,
        contact: Contact,
        tag: str,
        db: AsyncSession
    ) -> bool:
        """Add tag to contact"""
        try:
            if not contact.ghl_contact_id:
                logger.warning(f"No GHL contact ID for user {contact.id}")
                return False
            
            # Get current contact to retrieve existing tags
            contact_info = await self._make_request("GET", f"contacts/{contact.ghl_contact_id}")
            
            if not contact_info or "contact" not in contact_info:
                return False
            
            current_tags = contact_info["contact"].get("tags", [])
            
            if tag not in current_tags:
                current_tags.append(tag)
                
                update_data = {
                    "tags": current_tags
                }
                
                result = await self._make_request(
                    "PUT",
                    f"contacts/{contact.ghl_contact_id}",
                    data=update_data
                )
                
                if result:
                    logger.info(f"Added tag '{tag}' to GHL contact {contact.ghl_contact_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding GHL tag: {e}")
            return False
    
    async def remove_contact_tag(
        self,
        contact: Contact,
        tag: str,
        db: AsyncSession
    ) -> bool:
        """Remove tag from contact"""
        try:
            if not contact.ghl_contact_id:
                logger.warning(f"No GHL contact ID for user {contact.id}")
                return False
            
            # Get current contact to retrieve existing tags
            contact_info = await self._make_request("GET", f"contacts/{contact.ghl_contact_id}")
            
            if not contact_info or "contact" not in contact_info:
                return False
            
            current_tags = contact_info["contact"].get("tags", [])
            
            if tag in current_tags:
                current_tags.remove(tag)
                
                update_data = {
                    "tags": current_tags
                }
                
                result = await self._make_request(
                    "PUT",
                    f"contacts/{contact.ghl_contact_id}",
                    data=update_data
                )
                
                if result:
                    logger.info(f"Removed tag '{tag}' from GHL contact {contact.ghl_contact_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing GHL tag: {e}")
            return False
    
    async def create_webhook(
        self,
        webhook_url: str,
        events: List[str]
    ) -> Optional[str]:
        """Create webhook for GHL events"""
        try:
            webhook_data = {
                "url": webhook_url,
                "events": events,
                "locationId": self.location_id
            }
            
            result = await self._make_request("POST", "webhooks/", data=webhook_data)
            
            if result and "webhook" in result:
                webhook_id = result["webhook"]["id"]
                logger.info(f"Created GHL webhook {webhook_id}")
                return webhook_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating GHL webhook: {e}")
            return None
    
    async def get_contact_by_email(
        self,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """Get contact by email from GHL"""
        try:
            params = {
                "email": email,
                "locationId": self.location_id
            }
            
            result = await self._make_request("GET", "contacts/", params=params)
            
            if result and "contacts" in result and result["contacts"]:
                return result["contacts"][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting GHL contact by email: {e}")
            return None
    
    async def sync_contact_to_ghl(
        self,
        contact: Contact,
        db: AsyncSession
    ) -> bool:
        """Sync contact to GHL (create or update)"""
        try:
            if contact.ghl_contact_id:
                # Update existing contact
                return await self.update_contact(contact, db)
            else:
                # Create new contact
                ghl_contact_id = await self.create_contact(contact, db)
                return ghl_contact_id is not None
            
        except Exception as e:
            logger.error(f"Error syncing contact to GHL: {e}")
            return False
    
    async def handle_webhook(
        self,
        webhook_data: Dict[str, Any]
    ) -> bool:
        """Handle incoming webhook from GHL"""
        try:
            event_type = webhook_data.get("type")
            contact_data = webhook_data.get("contact", {})
            
            if event_type == "ContactCreate" or event_type == "ContactUpdate":
                # Handle contact creation/update
                email = contact_data.get("email")
                if email:
                    # Find local contact by email
                    # This would require a database query to find the contact
                    logger.info(f"Received GHL webhook for contact: {email}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling GHL webhook: {e}")
            return False
