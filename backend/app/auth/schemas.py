"""
Request/response schemas for the auth module.

Architecture:
    - Strict separation between input (request) and output (response) schemas.
    - password_hash is NEVER included in any response schema.
    - Pydantic v2 field validators handle trimming, normalization, and format
      checks before data reaches the service layer.
    - All schemas are pure Pydantic BaseModel — no Beanie dependency.
      This keeps the API contract decoupled from the database layer.

Design decisions:
    - Email normalization (lowercase + strip) prevents duplicate accounts
      caused by casing differences ("User@Mail.com" vs "user@mail.com").
    - Phone validation uses regex for E.164 format to ensure SMS gateway
      compatibility without importing a heavy phone-number library.
    - Password strength validation in the schema (min length) catches
      obvious weaknesses early. Full strength checks (uppercase, digits,
      special chars) are in core.security.validate_password_strength()
      and called by the service layer — keeps schema fast and service
      thorough.
    - UserUpdateRequest uses all-optional fields so clients can send
      partial updates (PATCH semantics). model_validator ensures at
      least one field is provided to prevent empty update requests.
    - UserResponse mirrors the User document but excludes password_hash,
      refresh_token_version, and metadata (internal fields).
    - ConfigDict(from_attributes=True) enables UserResponse.model_validate(user_doc)
      to work directly with Beanie Document instances.
"""

import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.auth.models import AccountStatus, LoginStatus, OTPPurpose, UserRole
from app.auth.security import TokenPair


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Minimum password length enforced at schema level.
# Full strength validation (uppercase, digit, special char) is in
# core.security.validate_password_strength() — called by the service layer.
_MIN_PASSWORD_LENGTH = 8
_MAX_PASSWORD_LENGTH = 128

# E.164 phone format: + followed by 10-14 digits.
# Covers all international phone numbers without a heavy library.
_PHONE_REGEX = re.compile(r"^\+[1-9]\d{9,14}$")

# Name pattern: letters, spaces, hyphens, apostrophes, and Unicode letters.
# Blocks numeric/special-char-only names while supporting international names.
_NAME_REGEX = re.compile(r"^[\w'\-\s]+$", re.UNICODE)


# ---------------------------------------------------------------------------
# Shared Validators
# ---------------------------------------------------------------------------

def _validate_name(value: str, field_name: str) -> str:
    """
    Strip whitespace, collapse internal spaces, and validate name format.

    Rejects:
        - Empty or whitespace-only strings (after stripping).
        - Names with digits or special characters (except hyphens/apostrophes).

    Used by: UserCreateRequest.first_name, last_name and UserUpdateRequest.
    """
    cleaned = " ".join(value.split())  # Collapse multiple spaces
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty or whitespace")
    if not _NAME_REGEX.match(cleaned):
        raise ValueError(
            f"{field_name} can only contain letters, spaces, hyphens, and apostrophes"
        )
    return cleaned


def _validate_phone(value: str) -> str:
    """
    Validate E.164 phone number format.

    E.164: + followed by country code and subscriber number (10-14 digits total).
    Examples: +919876543210 (India), +14155551234 (US).

    Returns the stripped value.
    """
    stripped = value.strip()
    if not _PHONE_REGEX.match(stripped):
        raise ValueError(
            "Phone number must be in E.164 format (e.g., +919876543210)"
        )
    return stripped


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class UserCreateRequest(BaseModel):
    """
    Registration payload — creates a new User document.

    All fields are required. Email and phone must be unique (enforced
    by the database unique indexes; the service layer should check
    before insert and raise ConflictException).

    Attributes:
        first_name: Given name. Trimmed and validated against name pattern.
        last_name: Family name. Trimmed and validated against name pattern.
        email: Primary login identifier. Normalized to lowercase.
        phone_number: Secondary login identifier. E.164 format required.
        password: Plain-text password. Min 8 chars at schema level;
                  full strength check in service layer via
                  core.security.validate_password_strength().
        role: Platform role. Defaults to CUSTOMER. ADMIN role assignment
              should be gated by an admin-only endpoint in the service layer.
    """

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's given name",
        examples=["Rajesh"],
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="User's family name",
        examples=["Kumar"],
    )
    email: EmailStr = Field(
        ...,
        description="Email address (unique, used for login)",
        examples=["rajesh.kumar@example.com"],
    )
    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=16,
        description="Phone in E.164 format",
        examples=["+919876543210"],
    )
    password: str = Field(
        ...,
        min_length=_MIN_PASSWORD_LENGTH,
        max_length=_MAX_PASSWORD_LENGTH,
        description=f"Password ({_MIN_PASSWORD_LENGTH}-{_MAX_PASSWORD_LENGTH} chars)",
        examples=["StrongP@ss1"],
    )
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="Platform role (defaults to customer)",
    )

    # --- Validators ---

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        return _validate_name(value, "First name")

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        return _validate_name(value, "Last name")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase email to prevent duplicate accounts from casing."""
        return value.strip().lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return _validate_phone(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Basic password checks at schema level.

        Rejects passwords that are entirely whitespace. Length is already
        enforced by min_length/max_length. Full strength validation
        (uppercase, digit, special char) is deferred to the service layer.
        """
        if not value.strip():
            raise ValueError("Password cannot be empty or whitespace")
        return value


class UserLoginRequest(BaseModel):
    """
    Login payload — authenticates via email + password.

    The service layer will:
        1. Find user by email.
        2. Verify password via core.security.verify_password().
        3. Check account_status (block INACTIVE/BLOCKED users).
        4. Update last_login timestamp.
        5. Return access + refresh tokens.

    Attributes:
        email: The user's registered email address.
        password: Plain-text password to verify against stored hash.
    """

    email: EmailStr = Field(
        ...,
        description="Registered email address",
        examples=["rajesh.kumar@example.com"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=_MAX_PASSWORD_LENGTH,
        description="Account password",
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Lowercase for consistent lookup against stored email."""
        return value.strip().lower()


class UserUpdateRequest(BaseModel):
    """
    Partial update payload — PATCH semantics.

    All fields are optional. At least one field must be provided.
    The service layer should validate authorization:
        - Users can update their own profile fields.
        - Only admins can change role or account_status.

    Attributes:
        first_name: Updated given name (trimmed, validated).
        last_name: Updated family name (trimmed, validated).
        phone_number: Updated phone (E.164, uniqueness checked by service).
        profile_image: Updated profile photo URL.
        role: Role change (admin-only operation).
        account_status: Status change (admin-only operation).
        metadata: Merge with existing metadata dict.
    """

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated given name",
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Updated family name",
    )
    phone_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=16,
        description="Updated phone in E.164 format",
    )
    profile_image: str | None = Field(
        default=None,
        max_length=512,
        description="Updated profile photo URL",
    )
    role: UserRole | None = Field(
        default=None,
        description="Role change (admin-only)",
    )
    account_status: AccountStatus | None = Field(
        default=None,
        description="Status change (admin-only)",
    )
    metadata: dict | None = Field(
        default=None,
        description="Key-value pairs to merge into user metadata",
    )

    # --- Validators ---

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_name(value, "First name")
        return value

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_name(value, "Last name")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is not None:
            return _validate_phone(value)
        return value

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UserUpdateRequest":
        """
        Reject empty update requests.

        Without this, a client could POST an empty body and trigger
        a no-op database write. This catches it at validation time.
        """
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError(
                "At least one field must be provided for update"
            )
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    """
    Public user representation — returned by all user-facing endpoints.

    Security:
        - password_hash: EXCLUDED (never sent to client).
        - refresh_token_version: EXCLUDED (internal token mechanism).
        - metadata: EXCLUDED (may contain sensitive internal data).

    ConfigDict(from_attributes=True) enables direct conversion from
    Beanie Document instances:
        response = UserResponse.model_validate(user_document)

    Attributes:
        id: MongoDB ObjectId as string.
        first_name: User's given name.
        last_name: User's family name.
        email: User's email address.
        phone_number: User's phone number.
        role: Platform role.
        account_status: Account lifecycle state.
        email_verified: Email verification status.
        phone_verified: Phone verification status.
        profile_completed: Profile completion status.
        profile_image: Profile photo URL (null if not uploaded).
        last_login: Last login timestamp (null if never logged in).
        created_at: Registration timestamp.
        updated_at: Last modification timestamp.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="User ID (MongoDB ObjectId)",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    first_name: str = Field(..., description="Given name")
    last_name: str = Field(..., description="Family name")
    email: EmailStr = Field(..., description="Email address")
    phone_number: str = Field(..., description="Phone number (E.164)")
    role: UserRole = Field(..., description="Platform role")
    account_status: AccountStatus = Field(..., description="Account state")
    email_verified: bool = Field(..., description="Email verified")
    phone_verified: bool = Field(..., description="Phone verified")
    profile_completed: bool = Field(..., description="Profile complete")
    profile_image: str | None = Field(None, description="Profile photo URL")
    last_login: datetime | None = Field(None, description="Last login time")
    created_at: datetime = Field(..., description="Registration time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """
        Convert Beanie's PydanticObjectId to a plain string.

        Beanie stores `id` as PydanticObjectId. API responses should
        return a plain string for frontend compatibility.
        """
        return str(value)


# ---------------------------------------------------------------------------
# Phase 3.2 Authentication API Schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    """
    Flexible login payload supporting either email address or E.164 phone number.
    """
    identifier: str = Field(
        ...,
        description="Registered email address OR phone number (+E.164 format)",
        examples=["rajesh.kumar@example.com", "+919876543210"],
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=_MAX_PASSWORD_LENGTH,
        description="Account password",
    )

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


class RefreshTokenRequest(BaseModel):
    """Payload containing a refresh token to rotate sessions."""
    refresh_token: str = Field(..., description="Current JWT refresh token")


class ChangePasswordRequest(BaseModel):
    """Payload to change an authenticated user's password."""
    current_password: str = Field(..., description="User's current password")
    new_password: str = Field(
        ...,
        min_length=_MIN_PASSWORD_LENGTH,
        max_length=_MAX_PASSWORD_LENGTH,
        description="New password meeting OWASP strength criteria",
    )


class ForgotPasswordRequest(BaseModel):
    """Payload to request a password reset link."""
    email: EmailStr = Field(..., description="Registered email address")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class ForgotPasswordResponse(BaseModel):
    """Response returned upon initiating password recovery."""
    message: str = Field(..., description="User-facing status message")
    reset_token: str = Field(..., description="Secure password reset token (development preview)")


class ResetPasswordRequest(BaseModel):
    """Payload to reset password using a recovery token."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=_MIN_PASSWORD_LENGTH,
        max_length=_MAX_PASSWORD_LENGTH,
        description="New password meeting OWASP strength criteria",
    )


class VerifyEmailRequest(BaseModel):
    """Payload to verify user email address."""
    token: str = Field(..., description="Email verification token")


class VerifyPhoneRequest(BaseModel):
    """Payload to verify user phone number via SMS OTP."""
    otp: str = Field(..., min_length=4, max_length=8, description="SMS OTP code")


class AuthResponse(BaseModel):
    """Authenticated session response containing profile and JWT tokens."""
    user: UserResponse
    tokens: TokenPair


class MessageResponse(BaseModel):
    """Generic status message response."""
    message: str
    success: bool = True


# =============================================================================
# OTP System Schemas (Phase 3.3)
# =============================================================================

class SendOTPRequest(BaseModel):
    """Payload to request an OTP code sent to an email or phone number."""
    identifier: str = Field(..., max_length=150, description="Email address or E.164 phone number")
    purpose: OTPPurpose = Field(..., description="Target purpose for OTP verification")

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


class VerifyOTPRequest(BaseModel):
    """Payload to verify a received 6-digit OTP code."""
    identifier: str = Field(..., max_length=150, description="Email address or E.164 phone number")
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$",
        description="6-digit numeric OTP code",
    )
    purpose: OTPPurpose = Field(..., description="Target purpose matching OTP generation")

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


class ResendOTPRequest(BaseModel):
    """Payload to request resending an unexpired OTP code."""
    identifier: str = Field(..., max_length=150, description="Email address or E.164 phone number")
    purpose: OTPPurpose = Field(..., description="Target purpose matching original OTP request")

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


class OTPResponse(BaseModel):
    """Response returned upon successfully sending or resending an OTP code."""
    success: bool = True
    message: str = Field(..., description="Status message")
    expires_in_seconds: int = Field(default=600, description="TTL in seconds until OTP expires")


class OTPLoginRequest(BaseModel):
    """Payload to authenticate via identifier and verified OTP code."""
    identifier: str = Field(..., max_length=150, description="Email address or E.164 phone number")
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$",
        description="6-digit numeric OTP code",
    )

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


# =============================================================================
# Session Management & Login History Schemas (Phase 3.3)
# =============================================================================

class SessionResponse(BaseModel):
    """Public representation of an active user session."""
    session_id: str
    ip_address: str | None
    device: str | None
    is_revoked: bool
    last_active: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LogoutDeviceRequest(BaseModel):
    """Payload to revoke a specific session by its session ID."""
    session_id: str = Field(..., description="UUID4 session identifier to log out")


class LoginHistoryResponse(BaseModel):
    """Public audit log entry for a user login attempt."""
    identifier: str
    status: LoginStatus
    failure_reason: str | None
    ip_address: str | None
    device: str | None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

