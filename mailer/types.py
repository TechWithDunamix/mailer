"""
Type definitions for the Nexios Mailer module.
"""

from typing import Dict, List, Optional, Union, Any, Literal
from pathlib import Path
from dataclasses import dataclass
from email.mime.base import MIMEBase

# Type aliases
EmailAddress = Union[str, List[str]]
EmailHeaders = Dict[str, str]
SecurityType = Literal["TLS", "SSL", "NONE"]

@dataclass
class EmailConfig:
    """Configuration for email server settings."""
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30
    max_retries: int = 3

@dataclass
class EmailAttachment:
    """Represents an email attachment."""
    file_path: Path
    filename: Optional[str] = None
    content_type: Optional[str] = None
    content_id: Optional[str] = None
    is_inline: bool = False

@dataclass
class EmailMessage:
    """Represents a complete email message."""
    to_emails: EmailAddress
    subject: str
    body: str
    is_html: bool = False
    from_email: Optional[str] = None
    cc_emails: Optional[EmailAddress] = None
    bcc_emails: Optional[EmailAddress] = None
    reply_to: Optional[str] = None
    headers: Optional[EmailHeaders] = None
    attachments: Optional[List[EmailAttachment]] = None
    template_data: Optional[Dict[str, Any]] = None

@dataclass
class EmailResult:
    """Result of email sending operation."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    recipients: Optional[List[str]] = None 