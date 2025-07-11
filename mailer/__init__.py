"""
Nexios Mailer Module

A comprehensive email sending solution for Nexios applications.
Supports SMTP, template rendering, attachments, and more.
"""

from typing import Dict, List, Optional, Union, Any
from pathlib import Path

from .base import SMTPMailer, EmailConfig, EmailMessage, EmailAttachment,send_quick_email
from .templates import EmailTemplate
from .utils import validate_email, sanitize_filename

__version__ = "1.0.0"
__all__ = [
    "SMTPMailer",
    "EmailConfig", 
    "EmailMessage",
    "EmailAttachment",
    "EmailTemplate",
    "validate_email",
    "sanitize_filename"
]

# Type aliases for better developer experience
EmailAddress = Union[str, List[str]]
EmailHeaders = Dict[str, str] 