"""
Beanie document models for Privacy, Compliance & Data Protection database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.privacy.schemas import (
    ConsentType,
    ExportFormat,
    PrivacyRequestStatus,
    PrivacyRequestType,
)


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class UserConsent(Document):
    """
    User consent preference document.

    Collection: user_consents
    """
    consent_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    consent_type: Annotated[ConsentType, Indexed()]
    is_granted: Annotated[bool, Indexed()] = True
    policy_version: str = "1.0"
    ip_address: str | None = None
    user_agent: str | None = None
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "user_consents"
        indexes = [
            "user_id",
            "consent_type",
            "is_granted",
        ]


class PrivacyRequest(Document):
    """
    User data access, export, or account deletion request.

    Collection: privacy_requests
    """
    request_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    request_type: Annotated[PrivacyRequestType, Indexed()]
    status: Annotated[PrivacyRequestStatus, Indexed()] = PrivacyRequestStatus.IN_PROGRESS
    grace_period_days: int = 30
    scheduled_deletion_at: datetime | None = None
    completion_notes: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)
    completed_at: datetime | None = None

    class Settings:
        name = "privacy_requests"
        indexes = [
            "user_id",
            "request_type",
            "status",
            "created_at",
        ]


class DataExport(Document):
    """
    Generated downloadable personal data export file metadata.

    Collection: data_exports
    """
    export_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    format: ExportFormat = ExportFormat.JSON
    export_data_summary: dict[str, Any] = Field(default_factory=dict)
    file_content: str = ""
    status: str = "ready"  # "ready", "expired"
    created_at: datetime = Field(default_factory=default_utc_now)
    expires_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "data_exports"
        indexes = [
            "user_id",
            "created_at",
        ]


class RetentionPolicy(Document):
    """
    Data retention rule definition.

    Collection: retention_policies
    """
    policy_key: Annotated[str, Indexed(unique=True)]
    category_name: str
    retention_days: int
    description: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "retention_policies"
        indexes = [
            "policy_key",
            "is_active",
        ]


class ComplianceRecord(Document):
    """
    Immutable compliance audit record.

    Collection: compliance_records
    """
    record_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    event_type: Annotated[str, Indexed()]
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "compliance_records"
        indexes = [
            "user_id",
            "event_type",
            "created_at",
        ]
