"""
Pydantic schemas for Customer Profile requests and responses.
"""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.customer.models import Gender
from app.utils.constants import PHONE_REGEX


class NotificationPreferencesSchema(BaseModel):
    """Notification channel preferences."""

    push: bool = True
    email: bool = True
    sms: bool = True


class UpdateCustomerProfileRequest(BaseModel):
    """Payload for updating customer profile details."""

    full_name: str | None = Field(default=None, min_length=2, max_length=100, description="Full name of customer")
    alternate_phone: str | None = Field(default=None, description="Optional secondary phone number (+91...)")
    date_of_birth: date | None = Field(default=None, description="Date of birth")
    gender: Gender | None = Field(default=None, description="Gender selection")
    preferred_language: str | None = Field(default=None, min_length=2, max_length=10, description="Language code (hi, en)")
    notification_preferences: NotificationPreferencesSchema | None = Field(default=None, description="Notification channels")
    addresses: list[dict[str, Any]] | None = Field(default=None, description="List of saved addresses")

    @field_validator("alternate_phone")
    @classmethod
    def validate_alternate_phone(cls, v: str | None) -> str | None:
        if v is not None and v.strip() != "":
            v_clean = v.strip()
            if not PHONE_REGEX.match(v_clean):
                raise ValueError("Invalid phone number format. Must start with +91 followed by 10 digits.")
            return v_clean
        return None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None:
            allowed = {"hi", "en", "mr", "ta", "te", "bn", "gu", "kn", "pa"}
            val = v.strip().lower()
            if val not in allowed:
                raise ValueError(f"Language '{v}' is not supported. Supported: {', '.join(sorted(allowed))}")
            return val
        return None


class CustomerProfileResponse(BaseModel):
    """Full customer profile DTO combining identity and profile fields."""

    id: str = Field(..., description="Customer Profile ObjectId string")
    user_id: str = Field(..., description="Linked User ObjectId string")
    email: str = Field(..., description="User primary email")
    phone: str = Field(..., description="User primary phone")
    full_name: str = Field(..., description="Customer full name")
    role: str = Field(default="customer", description="User role")

    profile_photo_url: str | None = None
    profile_photo_public_id: str | None = None
    alternate_phone: str | None = None
    date_of_birth: date | None = None
    gender: Gender | None = None
    preferred_language: str = "hi"
    notification_preferences: NotificationPreferencesSchema = Field(default_factory=NotificationPreferencesSchema)
    addresses: list[dict[str, Any]] = Field(default_factory=list)

    profile_completion_percentage: int = Field(..., ge=0, le=100, description="Calculated completion percentage (0-100)")
    profile_completed: bool = Field(default=False, description="True if completion threshold (>= 70%) is reached")

    created_at: datetime
    updated_at: datetime
