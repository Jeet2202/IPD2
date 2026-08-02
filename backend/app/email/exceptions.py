"""
Email module exceptions.

Architecture:
    - Inherits from base AppException so error handler catches and serializes.
    - Vendor-agnostic exception classes for email sending, configuration, and template errors.
"""

from app.core.exceptions import AppException


class EmailException(AppException):
    """Base exception for all email-related failures."""

    def __init__(
        self,
        message: str = "An error occurred in email processing",
        error_code: str = "EMAIL_ERROR",
        status_code: int = 500,
        details: list | None = None,
    ) -> None:
        super().__init__(message, error_code, status_code, details)


class EmailSendFailedException(EmailException):
    """Raised when an email provider fails to deliver a message."""

    def __init__(
        self,
        message: str = "Failed to send email message",
        details: list | None = None,
    ) -> None:
        super().__init__(message, "EMAIL_SEND_FAILED", 500, details)


class EmailProviderConfigException(EmailException):
    """Raised when email provider configuration (SMTP credentials, host) is missing or invalid."""

    def __init__(
        self,
        message: str = "Email provider configuration is missing or invalid",
        details: list | None = None,
    ) -> None:
        super().__init__(message, "EMAIL_CONFIG_INVALID", 500, details)
