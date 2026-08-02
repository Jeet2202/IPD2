"""
Customer profile Beanie document model — domain-specific data for customers.
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class Gender(str, Enum):
    """Gender options for customer profile."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class NotificationPreferences(BaseModel):
    """Channel-level notification opt-in/opt-out preferences."""

    push: bool = Field(default=True, description="Push notification channel enabled")
    email: bool = Field(default=True, description="Email notification channel enabled")
    sms: bool = Field(default=True, description="SMS notification channel enabled")


class CustomerProfile(Document):
    """
    Customer profile document linked 1:1 with User.

    Collection: customer_profiles
    """

    user_id: Annotated[PydanticObjectId, Indexed(unique=True)]

    profile_photo_url: str | None = Field(default=None, description="URL for profile photo")
    profile_photo_public_id: str | None = Field(default=None, description="Cloudinary public ID for profile photo")
    alternate_phone: str | None = Field(default=None, description="Optional secondary contact number")
    date_of_birth: date | None = Field(default=None, description="Date of birth")
    gender: Gender | None = Field(default=None, description="Gender identity")
    preferred_language: str = Field(default="hi", description="ISO 639-1 language preference code")
    notification_preferences: NotificationPreferences = Field(
        default_factory=NotificationPreferences,
        description="Notification channel preferences",
    )
    addresses: list[dict] = Field(default_factory=list, description="Saved customer addresses")
    profile_completed: bool = Field(default=False, description="True if profile completion threshold is reached")

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "customer_profiles"
        use_state_management = True

    async def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return await super().save(*args, **kwargs)
