"""
Production-Ready Swappable Email Architecture — Ally Auth Module.

Provides an Abstract Base Class (EmailProvider) with concrete implementations:
  1. SMTPEmailProvider: Sends real emails via SMTP using asyncio threadpool executor.
  2. ConsoleMockEmailProvider: Logs branded emails to console for local dev & test suites.

Includes reusable responsive HTML and plaintext email templates for all OTP verification workflows.
"""

import asyncio
import logging
import os
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.auth.models import OTPPurpose

logger = logging.getLogger(__name__)


# =============================================================================
# Abstract Base Class — Swappable Email Provider
# =============================================================================

class EmailProvider(ABC):
    """
    Abstract interface for sending transactional emails.
    Can be swapped seamlessly between SMTP, SendGrid, AWS SES, Resend, or Console Mock.
    """

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """
        Send an email asynchronously.

        Args:
            to_email: Target recipient address.
            subject: Email subject line.
            html_content: Responsive HTML template body.
            text_content: Plaintext fallback body.

        Returns:
            True if email dispatch succeeded, False otherwise.
        """
        ...


# =============================================================================
# Concrete Provider 1 — Standard SMTP Email Provider (asyncio to_thread)
# =============================================================================

class SMTPEmailProvider(EmailProvider):
    """
    Production SMTP provider using Python smtplib inside an asyncio threadpool executor
    to prevent blocking the ASGI event loop.
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        from_email: str = "no-reply@ally.com",
        use_tls: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls

    def _send_sync_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """Synchronous SMTP worker executed inside threadpool."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                if self.use_tls:
                    server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                server.send_message(msg)
            logger.info("SMTP email successfully sent to %s (Subject: %s)", to_email, subject)
            return True
        except Exception as exc:
            logger.error("Failed to send SMTP email to %s: %s", to_email, exc, exc_info=True)
            return False

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        return await asyncio.to_thread(
            self._send_sync_smtp,
            to_email,
            subject,
            html_content,
            text_content,
        )


# =============================================================================
# Concrete Provider 2 — Console Mock Provider (Dev & Testing)
# =============================================================================

class ConsoleMockEmailProvider(EmailProvider):
    """
    Development and test fallback provider that logs transactional emails to console.
    Requires no credentials or network access.
    """

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        logger.info(
            "\n%s\n[MOCK EMAIL DISPATCH]\nTo: %s\nSubject: %s\nBody:\n%s\n%s",
            "=" * 60,
            to_email,
            subject,
            text_content or html_content,
            "=" * 60,
        )
        return True


# =============================================================================
# Provider Factory
# =============================================================================

def get_email_provider() -> EmailProvider:
    """
    Resolve and return the appropriate EmailProvider instance based on environment variables.

    Reads:
      - EMAIL_PROVIDER: 'smtp' or 'console' (default: 'console' unless SMTP_HOST is present)
      - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL, SMTP_TLS
    """
    provider_type = os.getenv("EMAIL_PROVIDER", "").lower()
    smtp_host = os.getenv("SMTP_HOST")

    if provider_type == "smtp" or (not provider_type and smtp_host):
        return SMTPEmailProvider(
            host=smtp_host or "localhost",
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            from_email=os.getenv("FROM_EMAIL", "no-reply@ally.com"),
            use_tls=os.getenv("SMTP_TLS", "true").lower() == "true",
        )
    return ConsoleMockEmailProvider()


# =============================================================================
# Reusable Branded Email Templates
# =============================================================================

def get_otp_email_template(
    otp: str,
    purpose: OTPPurpose,
    expires_in_seconds: int,
) -> tuple[str, str, str]:
    """
    Generate responsive HTML and plaintext templates for an OTP code.

    Args:
        otp: 6-digit numeric OTP code.
        purpose: OTPPurpose enum value.
        expires_in_seconds: TTL in seconds.

    Returns:
        Tuple of (subject, html_content, text_content).
    """
    expires_minutes = max(1, expires_in_seconds // 60)

    purpose_titles = {
        OTPPurpose.REGISTRATION: "Welcome to Ally — Verify Your Account",
        OTPPurpose.LOGIN: "Your Ally Login Code",
        OTPPurpose.PASSWORD_RESET: "Reset Your Ally Password",
        OTPPurpose.EMAIL_VERIFY: "Verify Your Email Address",
        OTPPurpose.PHONE_VERIFY: "Verify Your Contact Information",
    }
    purpose_messages = {
        OTPPurpose.REGISTRATION: "Thank you for registering on Ally! Please use the OTP below to complete your registration.",
        OTPPurpose.LOGIN: "We received a login request for your Ally account. Use the OTP below to sign in.",
        OTPPurpose.PASSWORD_RESET: "We received a request to reset your Ally password. Use the OTP below to set a new password.",
        OTPPurpose.EMAIL_VERIFY: "Please verify your email address by entering the OTP below.",
        OTPPurpose.PHONE_VERIFY: "Please verify your phone number by entering the OTP below.",
    }

    subject = purpose_titles.get(purpose, "Your Ally Verification Code")
    message_text = purpose_messages.get(
        purpose, "Please use the OTP code below to verify your account."
    )

    text_content = (
        f"Ally — AI Powered Home Services Marketplace\n\n"
        f"{message_text}\n\n"
        f"Your Verification Code: {otp}\n\n"
        f"This code will expire in {expires_minutes} minutes. Do not share this OTP with anyone.\n"
        f"If you did not request this code, please ignore this email."
    )

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; margin: 0; padding: 24px; }}
        .container {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.06); padding: 32px; border: 1px solid #e2e8f0; }}
        .brand {{ font-size: 20px; font-weight: 700; color: #2563eb; margin-bottom: 24px; text-align: center; }}
        .title {{ font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 12px; }}
        .text {{ font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 24px; }}
        .otp-box {{ background-color: #f1f5f9; border: 2px dashed #94a3b8; border-radius: 8px; padding: 16px; text-align: center; margin-bottom: 24px; }}
        .otp-code {{ font-size: 28px; font-weight: 700; letter-spacing: 6px; color: #0f172a; }}
        .footer {{ font-size: 12px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="brand">Ally</div>
        <div class="title">{subject}</div>
        <p class="text">{message_text}</p>
        <div class="otp-box">
            <div class="otp-code">{otp}</div>
        </div>
        <p class="text">This code will expire in <strong>{expires_minutes} minutes</strong>. For your security, never share this OTP with anyone.</p>
        <div class="footer">
            &copy; 2026 Ally Technologies. All rights reserved.
        </div>
    </div>
</body>
</html>"""

    return subject, html_content, text_content
