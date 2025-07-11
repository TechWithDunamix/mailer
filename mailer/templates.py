"""
Email template rendering for the Nexios Mailer module.
"""

import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

class EmailTemplate:
    """
    Email template renderer using Jinja2.
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize template renderer.
        
        Args:
            template_dir: Directory containing email templates
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self.env = None
        
        if self.template_dir and self.template_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(self.template_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with context data.
        
        Args:
            template_name: Name of the template file
            context: Template context data
            
        Returns:
            Rendered template string
        """
        if not self.env:
            raise RuntimeError("Template directory not set or does not exist")
        
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template string with context data.
        
        Args:
            template_string: Template string content
            context: Template context data
            
        Returns:
            Rendered template string
        """
        template = Template(template_string)
        return template.render(**context)
    
    def render_html_email(self, 
                         template_name: str, 
                         context: Dict[str, Any],
                         subject_template: Optional[str] = None) -> tuple[str, str]:
        """
        Render an HTML email with optional subject template.
        
        Args:
            template_name: Name of the HTML template
            context: Template context data
            subject_template: Optional subject template string
            
        Returns:
            Tuple of (subject, html_body)
        """
        html_body = self.render_template(template_name, context)
        
        if subject_template:
            subject = self.render_string(subject_template, context)
        else:
            subject = context.get('subject', 'No Subject')
        
        return subject, html_body
    
    def render_text_email(self, 
                         template_name: str, 
                         context: Dict[str, Any],
                         subject_template: Optional[str] = None) -> tuple[str, str]:
        """
        Render a text email with optional subject template.
        
        Args:
            template_name: Name of the text template
            context: Template context data
            subject_template: Optional subject template string
            
        Returns:
            Tuple of (subject, text_body)
        """
        text_body = self.render_template(template_name, context)
        
        if subject_template:
            subject = self.render_string(subject_template, context)
        else:
            subject = context.get('subject', 'No Subject')
        
        return subject, text_body

# Common email templates
WELCOME_EMAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to {{app_name}}</title>
</head>
<body>
    <h1>Welcome to {{app_name}}!</h1>
    <p>Hello {{user_name}},</p>
    <p>Thank you for joining {{app_name}}. We're excited to have you on board!</p>
    <p>Best regards,<br>The {{app_name}} Team</p>
</body>
</html>
"""

WELCOME_EMAIL_TEXT = """
Welcome to {{app_name}}!

Hello {{user_name}},

Thank you for joining {{app_name}}. We're excited to have you on board!

Best regards,
The {{app_name}} Team
"""

PASSWORD_RESET_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset</title>
</head>
<body>
    <h1>Password Reset Request</h1>
    <p>Hello {{user_name}},</p>
    <p>You requested a password reset for your account.</p>
    <p>Click the link below to reset your password:</p>
    <a href="{{reset_link}}">Reset Password</a>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Best regards,<br>The {{app_name}} Team</p>
</body>
</html>
"""

PASSWORD_RESET_TEXT = """
Password Reset Request

Hello {{user_name}},

You requested a password reset for your account.

Click the link below to reset your password:
{{reset_link}}

If you didn't request this, please ignore this email.

Best regards,
The {{app_name}} Team
""" 