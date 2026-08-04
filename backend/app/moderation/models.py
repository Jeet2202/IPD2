"""
Beanie document models for Reporting, Moderation & Dispute Resolution database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.moderation.schemas import (
    DisputeStatus,
    DisputeType,
    ReportCategory,
    ReportStatus,
    ReportTargetType,
)
from app.trust.schemas import RiskLevel


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class PlatformReport(Document):
    """
    Platform violation / issue report document.

    Collection: reports
    """
    report_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    reporter_id: Annotated[str, Indexed()]
    target_type: ReportTargetType
    target_id: Annotated[str, Indexed()]
    category: Annotated[ReportCategory, Indexed()]
    description: str
    status: Annotated[ReportStatus, Indexed()] = ReportStatus.SUBMITTED
    severity: RiskLevel | None = None
    assigned_moderator_id: str | None = None
    resolution_action: str | None = None
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None

    class Settings:
        name = "reports"
        indexes = [
            "reporter_id",
            "target_id",
            "status",
            "category",
            "created_at",
        ]


class Dispute(Document):
    """
    Formal dispute case document.

    Collection: disputes
    """
    dispute_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    dispute_type: Annotated[DisputeType, Indexed()]
    booking_id: str | None = None
    initiator_id: Annotated[str, Indexed()]
    respondent_id: Annotated[str, Indexed()]
    reason: str
    status: Annotated[DisputeStatus, Indexed()] = DisputeStatus.SUBMITTED
    assigned_moderator_id: str | None = None
    resolution_decision: str | None = None
    administrative_action: str | None = None
    trust_score_delta: float = 0.0
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None

    class Settings:
        name = "disputes"
        indexes = [
            "initiator_id",
            "respondent_id",
            "status",
            "dispute_type",
            "created_at",
        ]


class ModerationCase(Document):
    """
    Internal moderator investigation case wrapper.

    Collection: moderation_cases
    """
    case_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    reference_id: Annotated[str, Indexed()]  # report_id or dispute_id
    reference_type: str  # "report" or "dispute"
    severity: RiskLevel = RiskLevel.MEDIUM
    assigned_moderator_id: Annotated[str | None, Indexed()] = None
    is_escalated: Annotated[bool, Indexed()] = False
    recommended_action: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "moderation_cases"
        indexes = [
            "reference_id",
            "assigned_moderator_id",
            "is_escalated",
        ]


class EvidenceFile(Document):
    """
    Uploaded evidence file metadata.

    Collection: evidence_files
    """
    evidence_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    case_id: Annotated[str, Indexed()]  # report_id or dispute_id
    uploader_id: Annotated[str, Indexed()]
    file_name: str
    file_type: str
    secure_url: str
    public_id: str
    description: str | None = None
    uploaded_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "evidence_files"
        indexes = [
            "case_id",
            "uploader_id",
            "uploaded_at",
        ]


class CaseNote(Document):
    """
    Timeline activity and investigation note on a report or dispute case.

    Collection: case_notes
    """
    note_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    case_id: Annotated[str, Indexed()]  # report_id or dispute_id
    author_id: str
    author_role: str
    note_text: str
    is_internal_only: bool = False
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "case_notes"
        indexes = [
            "case_id",
            "created_at",
        ]
