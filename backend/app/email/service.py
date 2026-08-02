"""
Email Service — business layer for email composition and delivery.

Architecture:
    - Provides high-level asynchronous domain methods for sending emails.
    - Integrates with EmailTemplateService to render responsive HTML and plain-text.
    - Delegates delivery to vendor-neutral BaseEmailProvider.
"""

import logging
from typing import Any

from app.core.config import settings
from app.email.provider import BaseEmailProvider, get_email_provider
from app.email.templates import EmailTemplateService

logger = logging.getLogger(__name__)


class EmailService:
    """
    Asynchronous high-level service for handling system email delivery.
    """

    def __init__(self, provider: BaseEmailProvider | None = None) -> None:
        self.provider = provider or get_email_provider()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
    ) -> bool:
        """
        Send a custom email.
        """
        return await self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments,
        )

    async def send_registration_otp(
        self,
        to_email: str,
        otp_code: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Render and deliver Registration OTP email.
        """
        rendered = EmailTemplateService.render_registration_otp(
            otp_code=otp_code,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES,
            user_name=user_name,
        )
        return await self.send_email(
            to_email=to_email,
            subject=rendered.subject,
            html_content=rendered.html_content,
            text_content=rendered.text_content,
        )

    async def send_login_otp(
        self,
        to_email: str,
        otp_code: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Render and deliver Login OTP email.
        """
        rendered = EmailTemplateService.render_login_otp(
            otp_code=otp_code,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES,
            user_name=user_name,
        )
        return await self.send_email(
            to_email=to_email,
            subject=rendered.subject,
            html_content=rendered.html_content,
            text_content=rendered.text_content,
        )

    async def send_password_reset_otp(
        self,
        to_email: str,
        otp_code: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Render and deliver Password Reset OTP email.
        """
        rendered = EmailTemplateService.render_password_reset_otp(
            otp_code=otp_code,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES,
            user_name=user_name,
        )
        return await self.send_email(
            to_email=to_email,
            subject=rendered.subject,
            html_content=rendered.html_content,
            text_content=rendered.text_content,
        )

    async def send_email_verification_otp(
        self,
        to_email: str,
        otp_code: str,
        user_name: str | None = None,
    ) -> bool:
        """
        Render and deliver Email Verification OTP email.
        """
        rendered = EmailTemplateService.render_email_verification_otp(
            otp_code=otp_code,
            expiry_minutes=settings.OTP_EXPIRY_MINUTES,
            user_name=user_name,
        )
        return await self.send_email(
            to_email=to_email,
            subject=rendered.subject,
            html_content=rendered.html_content,
            text_content=rendered.text_content,
        )


# Default singleton instance for convenience
email_service = EmailService()
