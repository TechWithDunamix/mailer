"""
Core email functionality for the Nexios Mailer module.
"""

import smtplib
import logging
import asyncio
import traceback
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

from .types import EmailConfig, EmailMessage, EmailAttachment, EmailResult, EmailAddress
from .utils import validate_emails, create_attachment, format_email_list

logger = logging.getLogger(__name__)

class SMTPMailer:
    """
    Enhanced SMTP mailer with better error handling and async support.
    """
    
    def __init__(self, config: EmailConfig):
        """
        Initialize the SMTP mailer with configuration.
        
        Args:
            config: Email configuration object
        """
        self.config = config
        self._server = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def connect(self) -> bool:
        """
        Connect to SMTP server.
        
        Returns:
            True if connection successful
        """
        try:
            if self.config.use_ssl:
                self._server = smtplib.SMTP_SSL(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
            else:
                self._server = smtplib.SMTP(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
                if self.config.use_tls:
                    self._server.starttls()
            
            self._server.login(self.config.smtp_user, self.config.smtp_pass)
            logger.info("Successfully connected to SMTP server")
            return True
            
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Failed to connect to SMTP server: {e}")
            return False
    
    def close(self):
        """Close SMTP connection."""
        if self._server:
            try:
                self._server.quit()
                logger.info("SMTP connection closed")
            except Exception as e:
                logger.warning(f"Error closing SMTP connection: {e}")
            finally:
                self._server = None
    
    def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send an email message.
        
        Args:
            message: Email message object
            
        Returns:
            EmailResult with success status and details
        """
        try:
            # Validate email addresses
            if not message.to_emails:
                raise ValueError("No recipient email addresses provided")
            to_emails = validate_emails(message.to_emails)
            cc_emails = validate_emails(message.cc_emails) if message.cc_emails else []
            bcc_emails = validate_emails(message.bcc_emails) if message.bcc_emails else []
            
            # Create message
            msg = MIMEMultipart()
            msg["From"] = message.from_email or self.config.smtp_user
            msg["To"] = format_email_list(to_emails)
            msg["Subject"] = message.subject
            
            if cc_emails:
                msg["Cc"] = format_email_list(cc_emails)
            if message.reply_to:
                msg["Reply-To"] = message.reply_to
            if message.headers:
                for key, value in message.headers.items():
                    msg[key] = value
            
            # Add body
            msg.attach(MIMEText(message.body, "html" if message.is_html else "plain"))
            
            # Add attachments
            if message.attachments:
                for attachment in message.attachments:
                    try:
                        mime_part = create_attachment(
                            attachment.file_path,
                            attachment.filename,
                            attachment.content_type
                        )
                        
                        if attachment.is_inline and attachment.content_id:
                            mime_part.add_header("Content-ID", f"<{attachment.content_id}>")
                            mime_part.add_header("Content-Disposition", "inline")
                        else:
                            mime_part.add_header("Content-Disposition", "attachment")
                        
                        msg.attach(mime_part)
                        
                    except Exception as e:
                        logger.warning(f"Failed to attach file {attachment.file_path}: {e}")
            
            # Connect and send
            if not self.connect():
                return EmailResult(
                    success=False,
                    error_message="Failed to connect to SMTP server"
                )
            
            # Send email
            all_recipients = to_emails + cc_emails + bcc_emails
            self._server.sendmail(
                self.config.smtp_user, 
                all_recipients, 
                msg.as_string()
            )
            
            logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return EmailResult(
                success=True,
                recipients=all_recipients
            )
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return EmailResult(
                success=False,
                error_message=str(e)
            )
        finally:
            self.close()
    
    def send_simple_email(self, 
                         to_emails: EmailAddress,
                         subject: str,
                         body: str,
                         is_html: bool = False,
                         **kwargs) -> EmailResult:
        """
        Send a simple email without complex attachments.
        
        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
            **kwargs: Additional EmailMessage parameters
            
        Returns:
            EmailResult with success status
        """
        message = EmailMessage(
            to_emails=to_emails,
            subject=subject,
            body=body,
            is_html=is_html,
            **kwargs
        )
        return self.send_email(message)
    
    async def send_email_async(self, message: EmailMessage) -> EmailResult:
        """
        Send email asynchronously.
        
        Args:
            message: Email message object
            
        Returns:
            EmailResult with success status
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send_email, message)
    
    async def send_simple_email_async(self,
                                    to_emails: EmailAddress,
                                    subject: str,
                                    body: str,
                                    is_html: bool = False,
                                    **kwargs) -> EmailResult:
        """
        Send a simple email asynchronously.
        
        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML
            **kwargs: Additional EmailMessage parameters
            
        Returns:
            EmailResult with success status
        """
        message = EmailMessage(
            to_emails=to_emails,
            subject=subject,
            body=body,
            is_html=is_html,
            **kwargs
        )
        return await self.send_email_async(message)

# Convenience function for quick email sending
def send_quick_email(config: EmailConfig,
                    to_emails: EmailAddress,
                    subject: str,
                    body: str,
                    is_html: bool = False,
                    **kwargs) -> EmailResult:
    """
    Quick function to send an email without creating a mailer instance.
    
    Args:
        config: Email configuration
        to_emails: Recipient email(s)
        subject: Email subject
        body: Email body
        is_html: Whether body is HTML
        **kwargs: Additional EmailMessage parameters
        
    Returns:
        EmailResult with success status
    """
    with SMTPMailer(config) as mailer:
        return mailer.send_simple_email(to_emails, subject, body, is_html, **kwargs)
    
    