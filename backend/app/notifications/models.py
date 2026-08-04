from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from beanie import Document, Indexed

class DeviceToken(Document):
    """
    Stores FCM device tokens for users.
    A single user can have multiple device tokens (e.g., phone and tablet).
    """
    user_id: Indexed(str) # type: ignore
    token: Indexed(str, unique=True) # type: ignore
    platform: str = "unknown" # ios, android, web
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "device_tokens"

class Notification(Document):
    """
    Stores notification metadata history.
    Payloads are not permanently stored; only metadata for the UI.
    Automatically deleted after 30 days via MongoDB TTL index.
    """
    user_id: Indexed(str) # type: ignore
    title: str
    body: str
    type: str # Booking Created, Worker Arriving, etc.
    data: Optional[dict] = None # Minimal routing data, e.g., {"booking_id": "..."}
    is_read: bool = False
    
    # TTL Index: expireAfterSeconds = 30 days (2592000 seconds)
    created_at: Indexed(datetime, expireAfterSeconds=2592000) = Field(default_factory=lambda: datetime.now(timezone.utc)) # type: ignore

    class Settings:
        name = "notifications"

class NotificationPreference(Document):
    """
    User preferences for push notifications.
    Created lazily when a user first attempts to update them, or with defaults.
    """
    user_id: Indexed(str, unique=True) # type: ignore
    booking_notifications: bool = True
    chat_notifications: bool = True
    ai_notifications: bool = True
    promotional_notifications: bool = False
    sound: bool = True
    vibration: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None # e.g., "22:00"
    quiet_hours_end: Optional[str] = None # e.g., "07:00"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "notification_preferences"
