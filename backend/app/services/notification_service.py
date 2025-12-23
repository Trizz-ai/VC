"""
Push notification service using Firebase Cloud Messaging
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.contact import Contact
from app.models.session import Session
from app.models.meeting import Meeting

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending push notifications"""
    
    def __init__(self):
        self.fcm_server_key = settings.FCM_SERVER_KEY
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        self.timeout = 30.0
    
    async def _send_fcm_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send FCM notification to device"""
        try:
            if not self.fcm_server_key:
                logger.warning("FCM not configured")
                return False
            
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": device_token,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default",
                    "badge": "1"
                }
            }
            
            if data:
                payload["data"] = data
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.fcm_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success") == 1:
                        logger.info(f"FCM notification sent to {device_token}")
                        return True
                    else:
                        logger.error(f"FCM notification failed: {result}")
                        return False
                else:
                    logger.error(f"FCM API error: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending FCM notification: {e}")
            return False
    
    async def send_meeting_reminder(
        self,
        contact: Contact,
        meeting: Meeting,
        device_token: str,
        hours_before: int = 24
    ) -> bool:
        """Send meeting reminder notification"""
        try:
            title = f"Meeting Reminder - {meeting.name}"
            body = f"Your meeting starts in {hours_before} hours at {meeting.address}"
            
            data = {
                "type": "meeting_reminder",
                "meeting_id": str(meeting.id),
                "meeting_name": meeting.name,
                "hours_before": hours_before
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending meeting reminder: {e}")
            return False
    
    async def send_check_in_reminder(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting,
        device_token: str
    ) -> bool:
        """Send check-in reminder notification"""
        try:
            title = "Time to Check In"
            body = f"Please check in for {meeting.name}"
            
            data = {
                "type": "check_in_reminder",
                "session_id": str(session.id),
                "meeting_id": str(meeting.id),
                "meeting_name": meeting.name
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending check-in reminder: {e}")
            return False
    
    async def send_check_out_reminder(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting,
        device_token: str
    ) -> bool:
        """Send check-out reminder notification"""
        try:
            title = "Time to Check Out"
            body = f"Please check out from {meeting.name}"
            
            data = {
                "type": "check_out_reminder",
                "session_id": str(session.id),
                "meeting_id": str(meeting.id),
                "meeting_name": meeting.name
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending check-out reminder: {e}")
            return False
    
    async def send_attendance_confirmation(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting,
        device_token: str
    ) -> bool:
        """Send attendance confirmation notification"""
        try:
            title = "Attendance Confirmed"
            body = f"Your attendance at {meeting.name} has been verified"
            
            data = {
                "type": "attendance_confirmation",
                "session_id": str(session.id),
                "meeting_id": str(meeting.id),
                "meeting_name": meeting.name
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending attendance confirmation: {e}")
            return False
    
    async def send_location_verification_failed(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting,
        device_token: str,
        reason: str
    ) -> bool:
        """Send location verification failed notification"""
        try:
            title = "Location Verification Failed"
            body = f"Could not verify your location for {meeting.name}. {reason}"
            
            data = {
                "type": "location_verification_failed",
                "session_id": str(session.id),
                "meeting_id": str(meeting.id),
                "meeting_name": meeting.name,
                "reason": reason
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending location verification failed: {e}")
            return False
    
    async def send_offline_sync_notification(
        self,
        contact: Contact,
        device_token: str,
        operation_count: int
    ) -> bool:
        """Send offline sync notification"""
        try:
            title = "Offline Data Synced"
            body = f"{operation_count} offline operations have been synced"
            
            data = {
                "type": "offline_sync",
                "operation_count": operation_count
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending offline sync notification: {e}")
            return False
    
    async def send_general_notification(
        self,
        contact: Contact,
        device_token: str,
        title: str,
        body: str,
        notification_type: str = "general"
    ) -> bool:
        """Send general notification"""
        try:
            data = {
                "type": notification_type
            }
            
            return await self._send_fcm_notification(
                device_token=device_token,
                title=title,
                body=body,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error sending general notification: {e}")
            return False
    
    async def send_bulk_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """Send notification to multiple devices"""
        try:
            if not self.fcm_server_key:
                logger.warning("FCM not configured")
                return {"success": 0, "failed": len(device_tokens)}
            
            headers = {
                "Authorization": f"key={self.fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "registration_ids": device_tokens,
                "notification": {
                    "title": title,
                    "body": body,
                    "sound": "default",
                    "badge": "1"
                }
            }
            
            if data:
                payload["data"] = data
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.fcm_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success_count = result.get("success", 0)
                    failure_count = result.get("failure", 0)
                    
                    logger.info(f"Bulk notification sent: {success_count} success, {failure_count} failed")
                    return {"success": success_count, "failed": failure_count}
                else:
                    logger.error(f"FCM bulk API error: {response.status_code} - {response.text}")
                    return {"success": 0, "failed": len(device_tokens)}
                    
        except Exception as e:
            logger.error(f"Error sending bulk notification: {e}")
            return {"success": 0, "failed": len(device_tokens)}
    
    async def schedule_notification(
        self,
        contact: Contact,
        meeting: Meeting,
        notification_time: datetime,
        device_token: str
    ) -> bool:
        """Schedule a notification for a specific time"""
        try:
            # This would typically use a job queue like Celery or RQ
            # For now, we'll just log the scheduled notification
            logger.info(f"Scheduled notification for {contact.email} at {notification_time}")
            
            # In a real implementation, you would:
            # 1. Store the notification in a database
            # 2. Use a job scheduler to send it at the specified time
            # 3. Handle timezone conversions properly
            
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            return False
