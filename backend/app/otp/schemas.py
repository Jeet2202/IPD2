"""
Pydantic v2 schemas for OTP generation and verification requests and responses.
"""

from typing import Any

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.utils.constants import OTP_REGEX, PHONE_REGEX


class GenerateOTPRequest(BaseModel):
    """Payload for requesting a new OTP."""

    email: EmailStr | None = None
    phone: str | None = None
    purpose: str = Field(..., description="Purpose: registration, login, password_reset, email_verification, phone_verification")
    channel: str = Field(default="email", description="Delivery channel: email or sms")

    @model_validator(mode="after")
    def validate_identifier(self) -> "GenerateOTPRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided to generate an OTP.")
        if self.phone and not PHONE_REGEX.match(self.phone):
            raise ValueError("Invalid Indian phone number format. Must start with +91 followed by 10 digits.")
        return self


class VerifyOTPRequest(BaseModel):
    """Payload for verifying an existing OTP."""

    email: EmailStr | None = None
    phone: str | None = None
    otp_code: str = Field(..., description="6-digit numeric OTP string")
    purpose: str = Field(..., description="Purpose matching the requested OTP")

    @model_validator(mode="after")
    def validate_request(self) -> "VerifyOTPRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided to verify OTP.")
        if not OTP_REGEX.match(self.otp_code.strip()):
            raise ValueError("OTP must be a 6-digit numeric code.")
        if self.phone and not PHONE_REGEX.match(self.phone):
            raise ValueError("Invalid Indian phone number format.")
        return self


class ResendOTPRequest(BaseModel):
    """Payload for requesting an OTP resend."""

    email: EmailStr | None = None
    phone: str | None = None
    purpose: str = Field(...)
    channel: str = Field(default="email")

    @model_validator(mode="after")
    def validate_identifier(self) -> "ResendOTPRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided to resend an OTP.")
        return self


class OTPResponse(BaseModel):
    """Standardized response for OTP generation and resend."""

    success: bool = True
    message: str
    expires_in_seconds: int
    resend_available_in_seconds: int = 60


class OTPVerificationResponse(BaseModel):
    """Standardized response for OTP verification."""

    success: bool = True
    message: str
    is_verified: bool = True
    data: dict[str, Any] | None = None
