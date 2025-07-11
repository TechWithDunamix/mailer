"""
Command-line interface for the Nexios Mailer module.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional
import click

from .base import EmailConfig, SMTPMailer, send_quick_email
from .templates import EmailTemplate
from .utils import validate_email

@click.group()
@click.version_option(version="1.0.0")
def main():
    """Nexios Mailer CLI - Send emails from the command line."""
    pass

@main.command()
@click.option("--to", "-t", required=True, help="Recipient email address")
@click.option("--subject", "-s", required=True, help="Email subject")
@click.option("--body", "-b", required=True, help="Email body")
@click.option("--html", is_flag=True, help="Send as HTML email")
@click.option("--config", "-c", help="Path to config file")
@click.option("--smtp-server", help="SMTP server hostname")
@click.option("--smtp-port", type=int, help="SMTP server port")
@click.option("--smtp-user", help="SMTP username")
@click.option("--smtp-pass", help="SMTP password")
@click.option("--use-tls", is_flag=True, default=True, help="Use TLS encryption")
@click.option("--use-ssl", is_flag=True, help="Use SSL encryption")
def send(to: str, subject: str, body: str, html: bool, config: Optional[str],
         smtp_server: Optional[str], smtp_port: Optional[int], smtp_user: Optional[str],
         smtp_pass: Optional[str], use_tls: bool, use_ssl: bool):
    """Send a simple email."""
    
    # Load config from file or environment
    email_config = load_config(config, smtp_server, smtp_port, smtp_user, smtp_pass, use_tls, use_ssl)
    
    if not email_config:
        click.echo("Error: SMTP configuration not found. Use --config or environment variables.", err=True)
        sys.exit(1)
    
    # Validate email
    if not validate_email(to):
        click.echo(f"Error: Invalid email address: {to}", err=True)
        sys.exit(1)
    
    # Send email
    result = send_quick_email(
        config=email_config,
        to_emails=to,
        subject=subject,
        body=body,
        is_html=html
    )
    
    if result.success:
        click.echo("✅ Email sent successfully!")
        if result.recipients:
            click.echo(f"📧 Sent to: {', '.join(result.recipients)}")
    else:
        click.echo(f"❌ Failed to send email: {result.error_message}", err=True)
        sys.exit(1)

@main.command()
@click.option("--template", "-t", required=True, help="Template name")
@click.option("--to", required=True, help="Recipient email address")
@click.option("--context", "-c", help="JSON context data")
@click.option("--template-dir", help="Template directory")
@click.option("--config", help="Path to config file")
@click.option("--smtp-server", help="SMTP server hostname")
@click.option("--smtp-port", type=int, help="SMTP server port")
@click.option("--smtp-user", help="SMTP username")
@click.option("--smtp-pass", help="SMTP password")
@click.option("--use-tls", is_flag=True, default=True, help="Use TLS encryption")
@click.option("--use-ssl", is_flag=True, help="Use SSL encryption")
def template(template: str, to: str, context: Optional[str], template_dir: Optional[str],
            config: Optional[str], smtp_server: Optional[str], smtp_port: Optional[int],
            smtp_user: Optional[str], smtp_pass: Optional[str], use_tls: bool, use_ssl: bool):
    """Send email using a template."""
    
    # Load config
    email_config = load_config(config, smtp_server, smtp_port, smtp_user, smtp_pass, use_tls, use_ssl)
    
    if not email_config:
        click.echo("Error: SMTP configuration not found.", err=True)
        sys.exit(1)
    
    # Load context
    template_context = {}
    if context:
        try:
            template_context = json.loads(context)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON context data.", err=True)
            sys.exit(1)
    
    # Create template renderer
    template_renderer = EmailTemplate(template_dir=template_dir)
    
    try:
        # Render template
        subject, html_body = template_renderer.render_html_email(
            template_name=template,
            context=template_context
        )
        
        # Send email
        result = send_quick_email(
            config=email_config,
            to_emails=to,
            subject=subject,
            body=html_body,
            is_html=True
        )
        
        if result.success:
            click.echo("✅ Template email sent successfully!")
        else:
            click.echo(f"❌ Failed to send template email: {result.error_message}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Template error: {e}", err=True)
        sys.exit(1)

@main.command()
@click.option("--config", "-c", help="Path to config file")
@click.option("--smtp-server", help="SMTP server hostname")
@click.option("--smtp-port", type=int, help="SMTP server port")
@click.option("--smtp-user", help="SMTP username")
@click.option("--smtp-pass", help="SMTP password")
@click.option("--use-tls", is_flag=True, default=True, help="Use TLS encryption")
@click.option("--use-ssl", is_flag=True, help="Use SSL encryption")
def test(config: Optional[str], smtp_server: Optional[str], smtp_port: Optional[int],
         smtp_user: Optional[str], smtp_pass: Optional[str], use_tls: bool, use_ssl: bool):
    """Test SMTP connection."""
    
    email_config = load_config(config, smtp_server, smtp_port, smtp_user, smtp_pass, use_tls, use_ssl)
    
    if not email_config:
        click.echo("Error: SMTP configuration not found.", err=True)
        sys.exit(1)
    
    click.echo("🔍 Testing SMTP connection...")
    
    try:
        with SMTPMailer(email_config) as mailer:
            if mailer.connect():
                click.echo("✅ SMTP connection successful!")
            else:
                click.echo("❌ SMTP connection failed!", err=True)
                sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Connection error: {e}", err=True)
        sys.exit(1)

def load_config(config_file: Optional[str], smtp_server: Optional[str], smtp_port: Optional[int],
                smtp_user: Optional[str], smtp_pass: Optional[str], use_tls: bool, use_ssl: bool) -> Optional[EmailConfig]:
    """Load email configuration from file or environment variables."""
    
    # Try to load from config file
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            return EmailConfig(
                smtp_server=config_data.get("smtp_server"),
                smtp_port=config_data.get("smtp_port", 587),
                smtp_user=config_data.get("smtp_user"),
                smtp_pass=config_data.get("smtp_pass"),
                use_tls=config_data.get("use_tls", True),
                use_ssl=config_data.get("use_ssl", False),
                timeout=config_data.get("timeout", 30),
                max_retries=config_data.get("max_retries", 3)
            )
        except Exception as e:
            click.echo(f"Warning: Could not load config file: {e}", err=True)
    
    # Try command line arguments
    if all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        return EmailConfig(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_pass=smtp_pass,
            use_tls=use_tls,
            use_ssl=use_ssl
        )
    
    # Try environment variables
    env_server = os.getenv("SMTP_SERVER")
    env_port = os.getenv("SMTP_PORT")
    env_user = os.getenv("SMTP_USER")
    env_pass = os.getenv("SMTP_PASS")
    
    if all([env_server, env_port, env_user, env_pass]):
        return EmailConfig(
            smtp_server=env_server,
            smtp_port=int(env_port),
            smtp_user=env_user,
            smtp_pass=env_pass,
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true",
            use_ssl=os.getenv("SMTP_USE_SSL", "false").lower() == "true"
        )
    
    return None

if __name__ == "__main__":
    main() 