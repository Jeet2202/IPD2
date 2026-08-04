"""
Pydantic v2 schemas for Authentication requests and responses.

Architecture:
    - Input validation schemas for all auth endpoints.
    - Output DTOs to serialize sanitized data to API clients/Flutter app.
    - Strict validation rules using pre-compiled regexes and constants.
    - Password strength validation via security utilities.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength
from app.utils.constants import (
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    PHONE_REGEX,
)
from app.utils.enums import UserRole


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    """Request payload for user registration."""

    email: EmailStr
    phone: str = Field(..., description="Indian phone number with country code, e.g. +919876543210")
    password: str = Field(..., description="Raw password string")
    first_name: str = Field(..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    last_name: str = Field(..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Role to register: customer or worker")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if v:
            v = v.strip()
            if len(v) == 10 and v.isdigit():
                v = f"+91{v}"
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid Indian phone number format. Must start with +91 followed by 10 digits.")
        return v

    @field_validator("role")
    @classmethod
    def validate_register_role(cls, v: UserRole) -> UserRole:
        if v not in (UserRole.CUSTOMER, UserRole.WORKER):
            raise ValueError("Registration is only allowed for customer or worker roles.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v


class LoginRequest(BaseModel):
    """Request payload for authentication via email or phone."""

    email: str | None = None
    phone: str | None = None
    password: str = Field(..., description="User password")
    role: UserRole | None = Field(default=None, description="Target role for strict login validation")

    device_id: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    operating_system: str | None = None
    browser: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("Invalid email address format.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip()
        if len(v) == 10 and v.isdigit():
            v = f"+91{v}"
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid Indian phone number format. Must start with +91 followed by 10 digits.")
        return v


class RefreshTokenRequest(BaseModel):
    """Request payload for token renewal."""

    refresh_token: str

    device_id: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    operating_system: str | None = None
    browser: str | None = None


class LogoutRequest(BaseModel):
    """Request payload for logging out current device."""

    refresh_token: str


class LogoutAllRequest(BaseModel):
    """Request payload for revoking all user sessions across devices."""

    pass


class ChangePasswordRequest(BaseModel):
    """Request payload for password change by authenticated user."""

    current_password: str = Field(..., description="Current account password")
    new_password: str = Field(..., description="New password string")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v


class DeleteAccountRequest(BaseModel):
    """Request payload for account deletion confirmation."""

    password: str = Field(..., description="Current password for identity verification")


class ForgotPasswordRequest(BaseModel):
    """Request payload for requesting password reset instructions."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request payload for applying new password via reset token."""

    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v


class VerifyEmailRequest(BaseModel):
    """Request payload for email verification via OTP."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class ResendEmailOTPRequest(BaseModel):
    """Request payload for resending an email OTP."""

    email: EmailStr
    purpose: str = Field(default="registration", description="OTP purpose: registration, login, password_reset")


class VerifyPasswordResetOTPRequest(BaseModel):
    """Request payload for verifying password reset OTP."""

    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class VerifyPhoneRequest(BaseModel):
    """Request payload for phone verification using OTP."""

    phone: str
    code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid Indian phone number format.")
        return v


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    """OAuth2 / JWT token response for Flutter & web clients."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class UserResponse(BaseModel):
    """Public user identity DTO without sensitive security fields."""

    id: str
    email: EmailStr
    phone: str
    full_name: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    is_phone_verified: bool
    account_status: str = Field(default="active", description="Status of user account: active or deactivated")
    verification_status: dict[str, bool] = Field(
        default_factory=dict,
        description="Verification flags for email and phone",
    )
    profile_status: str = Field(default="complete", description="User profile completion status")
    last_login: datetime | None = None
    created_at: datetime


class SessionResponse(BaseModel):
    """Active session DTO for session listing and revocation management."""

    id: str
    jti: str
    device_id: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    operating_system: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    last_used: datetime
    created_at: datetime
    is_current: bool = False


class MeResponse(BaseModel):
    """Current authenticated user details."""

    user: UserResponse


class SuccessResponse(BaseModel):
    """Generic successful operational response."""

    success: bool = True
    message: str
    data: dict[str, Any] | None = None


class ValidationErrorResponse(BaseModel):
    """Standardized validation error format."""

    success: bool = False
    error_code: str = "VALIDATION_ERROR"
    message: str = "Input validation failed"
    details: list[dict[str, Any]] = Field(default_factory=list)
