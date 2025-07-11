"""
Utility functions for the Nexios Mailer module.
"""

import re
import os
import mimetypes
from typing import List, Optional, Union
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_emails(emails: Union[str, List[str]]) -> List[str]:
    """
    Validate a list of email addresses.
    
    Args:
        emails: Single email or list of emails
        
    Returns:
        List of valid email addresses
        
    Raises:
        ValueError: If any email is invalid
    """
    if isinstance(emails, str):
        emails = [emails]
    
    valid_emails = []
    for email in emails:
        if not validate_email(email):
            raise ValueError(f"Invalid email address: {email}")
        valid_emails.append(email)
    
    return valid_emails

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe attachment.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(unsafe_chars, '_', filename)
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:255-len(ext)] + ext
    
    return sanitized

def get_content_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME content type for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME content type
    """
    file_path = Path(file_path)
    content_type, _ = mimetypes.guess_type(str(file_path))
    return content_type or 'application/octet-stream'

def create_attachment(file_path: Union[str, Path], 
                     filename: Optional[str] = None,
                     content_type: Optional[str] = None) -> MIMEBase:
    """
    Create a MIME attachment from a file.
    
    Args:
        file_path: Path to the file
        filename: Optional custom filename
        content_type: Optional content type
        
    Returns:
        MIMEBase attachment object
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if filename is None:
        filename = file_path.name
    
    if content_type is None:
        content_type = get_content_type(file_path)
    
    # Create MIME part
    part = MIMEBase(*content_type.split('/', 1))
    
    # Read and encode file
    with open(file_path, 'rb') as f:
        part.set_payload(f.read())
    
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    
    return part

def format_email_list(emails: Union[str, List[str]]) -> str:
    """
    Format email list for email headers.
    
    Args:
        emails: Single email or list of emails
        
    Returns:
        Comma-separated email string
    """
    if isinstance(emails, str):
        return emails
    return ', '.join(emails) 