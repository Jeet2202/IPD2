"""
Email infrastructure module.
"""

from app.email.exceptions import (
    EmailException,
    EmailProviderConfigException,
    EmailSendFailedException,
)
from app.email.provider import BaseEmailProvider, GmailSMTPProvider, get_email_provider
from app.email.service import EmailService, email_service
from app.email.templates import EmailTemplateService, RenderedEmail

__all__ = [
    "BaseEmailProvider",
    "GmailSMTPProvider",
    "get_email_provider",
    "EmailTemplateService",
    "RenderedEmail",
    "EmailService",
    "email_service",
    "EmailException",
    "EmailSendFailedException",
    "EmailProviderConfigException",
]
