"""
Email service using SendGrid
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.contact import Contact
from app.models.session import Session
from app.models.meeting import Meeting

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails via SendGrid"""
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.client = SendGridAPIClient(api_key=self.api_key) if self.api_key else None
    
    def _create_mail(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Mail:
        """Create SendGrid Mail object"""
        from_email = Email(self.from_email)
        to_email = To(to_email)
        
        if text_content:
            content = Content("text/plain", text_content)
        else:
            content = Content("text/html", html_content)
        
        mail = Mail(from_email, to_email, subject, content)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                mail.add_attachment(Attachment(
                    FileContent(attachment["content"]),
                    FileName(attachment["filename"]),
                    FileType(attachment["type"]),
                    Disposition(attachment.get("disposition", "attachment"))
                ))
        
        return mail
    
    async def send_welcome_email(
        self,
        contact: Contact
    ) -> bool:
        """Send welcome email to new user"""
        try:
            if not self.client:
                logger.warning("SendGrid not configured")
                return False
            
            subject = "Welcome to Verified Compliance"
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to Verified Compliance!</h2>
                <p>Hello {contact.first_name or 'there'},</p>
                <p>Thank you for registering with Verified Compliance. You can now track your attendance at meetings and events with GPS verification.</p>
                <p>Your account details:</p>
                <ul>
                    <li>Email: {contact.email}</li>
                    <li>Phone: {contact.phone or 'Not provided'}</li>
                    <li>Consent granted: {'Yes' if contact.consent_granted else 'No'}</li>
                </ul>
                <p>If you have any questions, please don't hesitate to contact us.</p>
                <p>Best regards,<br>The Verified Compliance Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to Verified Compliance!
            
            Hello {contact.first_name or 'there'},
            
            Thank you for registering with Verified Compliance. You can now track your attendance at meetings and events with GPS verification.
            
            Your account details:
            - Email: {contact.email}
            - Phone: {contact.phone or 'Not provided'}
            - Consent granted: {'Yes' if contact.consent_granted else 'No'}
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            The Verified Compliance Team
            """
            
            mail = self._create_mail(
                to_email=contact.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Welcome email sent to {contact.email}")
                return True
            else:
                logger.error(f"Failed to send welcome email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False
    
    async def send_attendance_confirmation(
        self,
        contact: Contact,
        session: Session,
        meeting: Meeting
    ) -> bool:
        """Send attendance confirmation email"""
        try:
            if not self.client:
                logger.warning("SendGrid not configured")
                return False
            
            subject = f"Attendance Confirmed - {meeting.name}"
            html_content = f"""
            <html>
            <body>
                <h2>Attendance Confirmed</h2>
                <p>Hello {contact.first_name or 'there'},</p>
                <p>Your attendance has been confirmed for:</p>
                <ul>
                    <li><strong>Meeting:</strong> {meeting.name}</li>
                    <li><strong>Location:</strong> {meeting.address}</li>
                    <li><strong>Check-in:</strong> {session.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if session.check_in_time else 'Not recorded'}</li>
                    <li><strong>Check-out:</strong> {session.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if session.check_out_time else 'Not recorded'}</li>
                </ul>
                <p>This attendance record has been verified with GPS location data.</p>
                <p>Thank you for your participation!</p>
                <p>Best regards,<br>The Verified Compliance Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Attendance Confirmed
            
            Hello {contact.first_name or 'there'},
            
            Your attendance has been confirmed for:
            - Meeting: {meeting.name}
            - Location: {meeting.address}
            - Check-in: {session.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if session.check_in_time else 'Not recorded'}
            - Check-out: {session.check_out_time.strftime('%Y-%m-%d %H:%M:%S') if session.check_out_time else 'Not recorded'}
            
            This attendance record has been verified with GPS location data.
            
            Thank you for your participation!
            
            Best regards,
            The Verified Compliance Team
            """
            
            mail = self._create_mail(
                to_email=contact.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Attendance confirmation sent to {contact.email}")
                return True
            else:
                logger.error(f"Failed to send attendance confirmation: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending attendance confirmation: {e}")
            return False
    
    async def send_meeting_reminder(
        self,
        contact: Contact,
        meeting: Meeting,
        hours_before: int = 24
    ) -> bool:
        """Send meeting reminder email"""
        try:
            if not self.client:
                logger.warning("SendGrid not configured")
                return False
            
            subject = f"Meeting Reminder - {meeting.name} (in {hours_before} hours)"
            html_content = f"""
            <html>
            <body>
                <h2>Meeting Reminder</h2>
                <p>Hello {contact.first_name or 'there'},</p>
                <p>This is a reminder that you have a meeting coming up:</p>
                <ul>
                    <li><strong>Meeting:</strong> {meeting.name}</li>
                    <li><strong>Description:</strong> {meeting.description or 'No description provided'}</li>
                    <li><strong>Location:</strong> {meeting.address}</li>
                    <li><strong>Start Time:</strong> {meeting.start_time.strftime('%Y-%m-%d %H:%M:%S') if meeting.start_time else 'TBD'}</li>
                    <li><strong>End Time:</strong> {meeting.end_time.strftime('%Y-%m-%d %H:%M:%S') if meeting.end_time else 'TBD'}</li>
                </ul>
                <p>Please arrive on time and ensure your GPS location services are enabled for attendance verification.</p>
                <p>Best regards,<br>The Verified Compliance Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Meeting Reminder
            
            Hello {contact.first_name or 'there'},
            
            This is a reminder that you have a meeting coming up:
            - Meeting: {meeting.name}
            - Description: {meeting.description or 'No description provided'}
            - Location: {meeting.address}
            - Start Time: {meeting.start_time.strftime('%Y-%m-%d %H:%M:%S') if meeting.start_time else 'TBD'}
            - End Time: {meeting.end_time.strftime('%Y-%m-%d %H:%M:%S') if meeting.end_time else 'TBD'}
            
            Please arrive on time and ensure your GPS location services are enabled for attendance verification.
            
            Best regards,
            The Verified Compliance Team
            """
            
            mail = self._create_mail(
                to_email=contact.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Meeting reminder sent to {contact.email}")
                return True
            else:
                logger.error(f"Failed to send meeting reminder: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending meeting reminder: {e}")
            return False
    
    async def send_password_reset(
        self,
        contact: Contact,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        try:
            if not self.client:
                logger.warning("SendGrid not configured")
                return False
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            subject = "Password Reset Request"
            html_content = f"""
            <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>Hello {contact.first_name or 'there'},</p>
                <p>You have requested to reset your password for your Verified Compliance account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <p>This link will expire in 24 hours.</p>
                <p>Best regards,<br>The Verified Compliance Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Password Reset Request
            
            Hello {contact.first_name or 'there'},
            
            You have requested to reset your password for your Verified Compliance account.
            
            Click the link below to reset your password:
            {reset_url}
            
            If you didn't request this password reset, please ignore this email.
            This link will expire in 24 hours.
            
            Best regards,
            The Verified Compliance Team
            """
            
            mail = self._create_mail(
                to_email=contact.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Password reset email sent to {contact.email}")
                return True
            else:
                logger.error(f"Failed to send password reset email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return False
    
    async def send_attendance_report(
        self,
        contact: Contact,
        attendance_data: Dict[str, Any]
    ) -> bool:
        """Send attendance report email"""
        try:
            if not self.client:
                logger.warning("SendGrid not configured")
                return False
            
            subject = "Your Attendance Report"
            html_content = f"""
            <html>
            <body>
                <h2>Attendance Report</h2>
                <p>Hello {contact.first_name or 'there'},</p>
                <p>Here is your attendance summary:</p>
                <ul>
                    <li><strong>Total Sessions:</strong> {attendance_data.get('total_sessions', 0)}</li>
                    <li><strong>Completed Sessions:</strong> {attendance_data.get('completed_sessions', 0)}</li>
                    <li><strong>Average Duration:</strong> {attendance_data.get('average_duration_minutes', 0):.1f} minutes</li>
                </ul>
                <p>Thank you for your consistent participation!</p>
                <p>Best regards,<br>The Verified Compliance Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Attendance Report
            
            Hello {contact.first_name or 'there'},
            
            Here is your attendance summary:
            - Total Sessions: {attendance_data.get('total_sessions', 0)}
            - Completed Sessions: {attendance_data.get('completed_sessions', 0)}
            - Average Duration: {attendance_data.get('average_duration_minutes', 0):.1f} minutes
            
            Thank you for your consistent participation!
            
            Best regards,
            The Verified Compliance Team
            """
            
            mail = self._create_mail(
                to_email=contact.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            response = self.client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Attendance report sent to {contact.email}")
                return True
            else:
                logger.error(f"Failed to send attendance report: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending attendance report: {e}")
            return False
