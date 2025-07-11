# Nexios Mailer Module

A comprehensive, type-safe email sending solution for Nexios applications. Built with modern Python features, async support, and excellent developer experience.

## Features

- ✅ **Type-safe**: Full type hints and dataclass support
- ✅ **Async support**: Both sync and async email sending
- ✅ **Template rendering**: Jinja2 template support
- ✅ **Attachment handling**: File attachments and inline images
- ✅ **Error handling**: Comprehensive error handling and logging
- ✅ **Context managers**: Automatic connection management
- ✅ **Validation**: Email address validation and sanitization
- ✅ **Flexible**: Support for multiple SMTP providers

## Quick Start

### Basic Usage

```python
from mailer import EmailConfig, SMTPMailer, send_quick_email

# Configure your email settings
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_pass="your-app-password",
    use_tls=True
)

# Quick send (recommended for simple emails)
result = send_quick_email(
    config=config,
    to_emails="recipient@example.com",
    subject="Hello from Nexios!",
    body="This is a test email.",
    is_html=False
)

if result.success:
    print("Email sent successfully!")
else:
    print(f"Failed to send email: {result.error_message}")
```

### Using the Mailer Class

```python
from mailer import EmailConfig, SMTPMailer, EmailMessage

# Create mailer instance
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_pass="your-app-password",
    use_tls=True
)

# Use as context manager (recommended)
with SMTPMailer(config) as mailer:
    message = EmailMessage(
        to_emails=["user1@example.com", "user2@example.com"],
        subject="Welcome to our platform!",
        body="<h1>Welcome!</h1><p>We're glad to have you on board.</p>",
        is_html=True,
        cc_emails="admin@example.com",
        reply_to="support@example.com"
    )
    
    result = mailer.send_email(message)
    
    if result.success:
        print(f"Email sent to {len(result.recipients)} recipients")
    else:
        print(f"Failed: {result.error_message}")
```

## Advanced Features

### Template Rendering

```python
from mailer import EmailTemplate, EmailConfig, SMTPMailer

# Create template renderer
template = EmailTemplate(template_dir="email_templates")

# Render HTML email
context = {
    "user_name": "John Doe",
    "app_name": "MyApp",
    "subject": "Welcome to MyApp!"
}

subject, html_body = template.render_html_email(
    template_name="welcome.html",
    context=context
)

# Send with template
config = EmailConfig(...)
with SMTPMailer(config) as mailer:
    result = mailer.send_simple_email(
        to_emails="user@example.com",
        subject=subject,
        body=html_body,
        is_html=True
    )
```

### Attachments

```python
from mailer import EmailMessage, EmailAttachment
from pathlib import Path

# Create message with attachments
message = EmailMessage(
    to_emails="user@example.com",
    subject="Monthly Report",
    body="Please find the attached monthly report.",
    attachments=[
        EmailAttachment(
            file_path=Path("reports/monthly.pdf"),
            filename="Monthly_Report_2024.pdf"
        ),
        EmailAttachment(
            file_path=Path("images/logo.png"),
            content_id="logo",
            is_inline=True
        )
    ]
)

with SMTPMailer(config) as mailer:
    result = mailer.send_email(message)
```

### Async Support

```python
import asyncio
from mailer import EmailConfig, SMTPMailer

async def send_welcome_emails():
    config = EmailConfig(...)
    mailer = SMTPMailer(config)
    
    users = ["user1@example.com", "user2@example.com", "user3@example.com"]
    
    # Send emails concurrently
    tasks = []
    for user in users:
        task = mailer.send_simple_email_async(
            to_emails=user,
            subject="Welcome!",
            body="Welcome to our platform!"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        if result.success:
            print("Email sent successfully")
        else:
            print(f"Failed: {result.error_message}")

# Run async function
asyncio.run(send_welcome_emails())
```

## Configuration

### EmailConfig Options

```python
from mailer import EmailConfig

config = EmailConfig(
    smtp_server="smtp.gmail.com",    # SMTP server hostname
    smtp_port=587,                   # SMTP port (587 for TLS, 465 for SSL)
    smtp_user="your-email@gmail.com", # SMTP username
    smtp_pass="your-app-password",   # SMTP password
    use_tls=True,                    # Use TLS encryption
    use_ssl=False,                   # Use SSL encryption
    timeout=30,                      # Connection timeout in seconds
    max_retries=3                    # Maximum retry attempts
)
```

### Popular SMTP Providers

#### Gmail
```python
config = EmailConfig(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_pass="your-app-password",  # Use App Password, not regular password
    use_tls=True
)
```

#### Outlook/Hotmail
```python
config = EmailConfig(
    smtp_server="smtp-mail.outlook.com",
    smtp_port=587,
    smtp_user="your-email@outlook.com",
    smtp_pass="your-password",
    use_tls=True
)
```

#### Zoho
```python
config = EmailConfig(
    smtp_server="smtp.zoho.com",
    smtp_port=587,
    smtp_user="your-email@yourdomain.com",
    smtp_pass="your-password",
    use_tls=True
)
```

## Template Examples

### HTML Template (`welcome.html`)
```html
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
    
    {% if user_role %}
    <p>Your role: {{user_role}}</p>
    {% endif %}
    
    <p>Best regards,<br>The {{app_name}} Team</p>
</body>
</html>
```

### Text Template (`welcome.txt`)
```
Welcome to {{app_name}}!

Hello {{user_name}},

Thank you for joining {{app_name}}. We're excited to have you on board!

{% if user_role %}
Your role: {{user_role}}
{% endif %}

Best regards,
The {{app_name}} Team
```

## Error Handling

```python
from mailer import EmailConfig, SMTPMailer

config = EmailConfig(...)

try:
    with SMTPMailer(config) as mailer:
        result = mailer.send_simple_email(
            to_emails="invalid-email",
            subject="Test",
            body="Test"
        )
        
        if not result.success:
            print(f"Email failed: {result.error_message}")
            
except ValueError as e:
    print(f"Invalid email address: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Integration with Nexios

### In a Nexios Route

```python
from nexios import Nexios
from mailer import EmailConfig, send_quick_email

app = Nexios()

@app.post("/send-welcome")
async def send_welcome_email(request):
    data = await request.json()
    
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_user="your-email@gmail.com",
        smtp_pass="your-app-password",
        use_tls=True
    )
    
    result = send_quick_email(
        config=config,
        to_emails=data["email"],
        subject="Welcome to our platform!",
        body=f"Hello {data['name']}, welcome to our platform!",
        is_html=False
    )
    
    if result.success:
        return {"message": "Welcome email sent successfully"}
    else:
        return {"error": result.error_message}, 400
```

### With Dependency Injection

```python
from nexios import Nexios
from mailer import EmailConfig, SMTPMailer

app = Nexios()

# Configure mailer as a dependency
def get_mailer():
    config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_user="your-email@gmail.com",
        smtp_pass="your-app-password",
        use_tls=True
    )
    return SMTPMailer(config)

@app.post("/send-notification")
async def send_notification(request, mailer: SMTPMailer = get_mailer):
    data = await request.json()
    
    result = mailer.send_simple_email(
        to_emails=data["email"],
        subject="New Notification",
        body=data["message"],
        is_html=True
    )
    
    return {"success": result.success}
```

## Best Practices

1. **Use context managers**: Always use `with SMTPMailer(config) as mailer:` for automatic connection management
2. **Validate emails**: The module automatically validates email addresses
3. **Handle errors**: Always check `result.success` and handle errors appropriately
4. **Use templates**: For repeated emails, use templates instead of hardcoded strings
5. **Async for bulk**: Use async methods when sending to multiple recipients
6. **Secure credentials**: Store SMTP credentials in environment variables

## Environment Variables

```python
import os
from mailer import EmailConfig

config = EmailConfig(
    smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    smtp_port=int(os.getenv("SMTP_PORT", "587")),
    smtp_user=os.getenv("SMTP_USER"),
    smtp_pass=os.getenv("SMTP_PASS"),
    use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
)
```

## Contributing

The mailer module is designed to be extensible. You can:

- Add new email providers
- Create custom template engines
- Add new attachment types
- Implement email queuing
- Add email tracking features

## License

This module is part of the Nexios framework and follows the same license terms. 