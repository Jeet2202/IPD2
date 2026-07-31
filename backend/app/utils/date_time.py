"""
Timezone-aware datetime utilities.

Every datetime in this application MUST be UTC. This module provides
helper functions that enforce UTC consistently, so feature modules
never deal with naive datetimes or timezone confusion.

MongoDB stores datetimes in UTC internally. Pydantic v2 serializes
datetime objects with timezone info. This module bridges both.

Rules:
    - Use utc_now() instead of datetime.now() or datetime.utcnow()
    - Store all datetimes as UTC in MongoDB
    - Convert to local timezone ONLY in the API response layer
    - Use TimestampMixin in Beanie models for created_at/updated_at
"""

from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# UTC Helpers
# ---------------------------------------------------------------------------

def utc_now() -> datetime:
    """
    Return the current time as a timezone-aware UTC datetime.

    Use this instead of:
        - datetime.now()      ← naive, uses local timezone
        - datetime.utcnow()   ← naive, no timezone info attached
        - datetime.now(UTC)    ← correct but verbose

    Returns:
        Timezone-aware datetime in UTC.
    """
    return datetime.now(timezone.utc)


def utc_from_timestamp(ts: float) -> datetime:
    """
    Convert a Unix timestamp to a timezone-aware UTC datetime.

    Args:
        ts: Unix timestamp (seconds since epoch).

    Returns:
        Timezone-aware datetime in UTC.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_iso(dt: datetime) -> str:
    """
    Format a datetime as ISO 8601 string.

    Output: '2026-01-15T10:30:00+00:00'

    Args:
        dt: The datetime to format.

    Returns:
        ISO 8601 formatted string.
    """
    return dt.isoformat()


def format_human(dt: datetime) -> str:
    """
    Format a datetime as a human-readable string.

    Output: '15 Jan 2026, 10:30 AM'

    Args:
        dt: The datetime to format.

    Returns:
        Human-readable date string.
    """
    return dt.strftime("%d %b %Y, %I:%M %p")


# ---------------------------------------------------------------------------
# Time Differences
# ---------------------------------------------------------------------------

def time_ago(dt: datetime) -> str:
    """
    Convert a datetime to a human-readable relative time string.

    Output: '5 minutes ago', '2 hours ago', '3 days ago'

    Used in notification displays and activity feeds.

    Args:
        dt: The past datetime to compare against now.

    Returns:
        Human-readable relative time string.
    """
    now = utc_now()

    # Ensure both are timezone-aware for comparison
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 0:
        return "just now"
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    if seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    if seconds < 31536000:  # 365 days
        months = seconds // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"

    years = seconds // 31536000
    return f"{years} year{'s' if years != 1 else ''} ago"


def is_expired(dt: datetime, ttl_seconds: int) -> bool:
    """
    Check if a datetime has expired based on a TTL.

    Usage:
        if is_expired(otp.created_at, OTP_EXPIRY_SECONDS):
            raise BadRequestException("OTP expired")

    Args:
        dt: The creation datetime.
        ttl_seconds: Time-to-live in seconds.

    Returns:
        True if the datetime is older than ttl_seconds.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return utc_now() > dt + timedelta(seconds=ttl_seconds)


# ---------------------------------------------------------------------------
# Timestamp Mixin for Beanie Models
# ---------------------------------------------------------------------------

class TimestampMixin(BaseModel):
    """
    Pydantic mixin that adds created_at and updated_at fields.

    Inherit this in Beanie Document models to automatically track
    creation and modification timestamps.

    Usage:
        class Worker(Document, TimestampMixin):
            name: str
            phone: str
            # created_at and updated_at come from TimestampMixin

    Note: updated_at must be set manually in update operations:
        worker.updated_at = utc_now()
        await worker.save()
    """
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
