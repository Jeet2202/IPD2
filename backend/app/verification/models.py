"""
Beanie document models for Worker Verification & Trust Management database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.verification.schemas import (
    TrustBadgeType,
    VerificationStatus,
    VerificationType,
)


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class WorkerVerification(Document):
    """
    Worker verification request lifecycle entity.

    Collection: worker_verifications
    """
    verification_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    worker_id: Annotated[str, Indexed()]
    verification_type: VerificationType = VerificationType.IDENTITY
    status: VerificationStatus = VerificationStatus.DRAFT
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewer_id: str | None = None
    review_notes: str | None = None
    document_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "worker_verifications"
        indexes = [
            "worker_id",
            "verification_type",
            "status",
            "created_at",
        ]


class VerificationDocument(Document):
    """
    Document metadata and Cloudinary storage reference.

    Collection: verification_documents
    """
    document_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    worker_id: Annotated[str, Indexed()]
    verification_id: Annotated[str | None, Indexed()] = None
    document_type: str  # e.g., "aadhaar", "pan", "driving_license", "address_proof", "skill_certificate"
    document_number: str | None = None
    secure_url: str
    public_id: str
    version: int = 1
    status: VerificationStatus = VerificationStatus.DRAFT
    file_name: str
    file_size: int = 0
    mime_type: str = "application/octet-stream"
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "verification_documents"
        indexes = [
            "worker_id",
            "document_type",
            "status",
        ]


class VerificationReview(Document):
    """
    Audit record of administrative verification reviews and decisions.

    Collection: verification_reviews
    """
    review_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    verification_id: Annotated[str, Indexed()]
    worker_id: Annotated[str, Indexed()]
    reviewer_id: Annotated[str, Indexed()]
    action: str  # "started_review", "approved", "rejected", "requested_resubmission"
    review_notes: str | None = None
    previous_status: VerificationStatus
    new_status: VerificationStatus
    reviewed_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "verification_reviews"
        indexes = [
            "verification_id",
            "worker_id",
            "reviewer_id",
            "reviewed_at",
        ]


class VerificationBadge(Document):
    """
    Earned trust badge assigned to a worker profile.

    Collection: verification_badges
    """
    badge_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    worker_id: Annotated[str, Indexed()]
    badge_type: TrustBadgeType
    badge_name: str
    description: str
    icon_url: str | None = None
    granted_at: datetime = Field(default_factory=default_utc_now)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "verification_badges"
        indexes = [
            "worker_id",
            "badge_type",
            "is_active",
        ]
