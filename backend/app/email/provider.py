"""
Email Provider Abstraction & SMTP Implementation using aiosmtplib.

Architecture:
    - BaseEmailProvider: Abstract Base Class (ABC) defining the provider contract.
      Allows swapping Gmail SMTP for Resend, SendGrid, or AWS SES without changing business logic.
    - GmailSMTPProvider: Production-ready async SMTP provider utilizing aiosmtplib.
    - Factory function get_email_provider() resolves configured provider.
"""

from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
from typing import Any

import aiosmtplib

from app.core.config import settings
from app.email.exceptions import EmailProviderConfigException, EmailSendFailedException

logger = logging.getLogger(__name__)


class BaseEmailProvider(ABC):
    """Abstract interface for all email delivery providers."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> bool:
        """
        Send an email message asynchronously.

        Args:
            to_email: Target recipient email address.
            subject: Email subject header.
            html_content: HTML message body.
            text_content: Plain-text fallback message body.
            attachments: Optional list of file attachments.

        Returns:
            True if delivered successfully.

        Raises:
            EmailSendFailedException: Delivery failure.
            EmailProviderConfigException: Missing or bad credentials.
        """
        pass


class GmailSMTPProvider(BaseEmailProvider):
    """
    Async SMTP email provider using aiosmtplib for Gmail / custom SMTP servers.
    """

    def __init__(self) -> None:
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = (
            settings.SMTP_PASSWORD.get_secret_value()
            if settings.SMTP_PASSWORD
            else None
        )
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    def _validate_config(self) -> None:
        """Validate SMTP credentials before sending."""
        if not self.username or not self.password:
            # In development/test mode without credentials, log warning instead of crashing
            if not settings.is_production:
                logger.warning(
                    "SMTP credentials missing. Email delivery will be simulated in non-production mode."
                )
                return
            raise EmailProviderConfigException(
                message="SMTP_USERNAME and SMTP_PASSWORD must be configured for email delivery."
            )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> bool:
        """
        Deliver an HTML / plain-text email using aiosmtplib.
        """
        self._validate_config()

        # If credentials are not configured in non-production, log and simulate delivery
        if not self.username or not self.password:
            logger.info(
                "[SIMULATED EMAIL] To: %s | Subject: %s | Provider: GmailSMTP",
                to_email,
                subject,
            )
            return True

        # Build multipart message
        message = MIMEMultipart("alternative")
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Attach plain-text fallback
        plain_text = text_content or "Please view this email in an HTML-compatible client."
        message.attach(MIMEText(plain_text, "plain", "utf-8"))

        # Attach HTML content
        message.attach(MIMEText(html_content, "html", "utf-8"))

        # Send via aiosmtplib
        try:
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True,
            )
            logger.info("Email delivered successfully to %s", to_email)
            return True
        except aiosmtplib.SMTPException as exc:
            logger.error("SMTP delivery failure to %s: %s", to_email, str(exc))
            raise EmailSendFailedException(
                message=f"Failed to send email to {to_email}",
                details=[str(exc)],
            )
        except Exception as exc:
            logger.error("Unexpected error delivering email to %s: %s", to_email, str(exc))
            raise EmailSendFailedException(
                message=f"Unexpected error delivering email to {to_email}",
                details=[str(exc)],
            )


def get_email_provider() -> BaseEmailProvider:
    """
    Factory function resolving configured email provider.
    Currently defaults to GmailSMTPProvider. Swappable via settings.EMAIL_PROVIDER.
    """
    provider_type = settings.EMAIL_PROVIDER.lower()
    if provider_type in ("smtp", "gmail"):
        return GmailSMTPProvider()
    
    # Fallback to GmailSMTPProvider for extensibility
    return GmailSMTPProvider()
