"""
Pydantic v2 schemas and Enums for Worker Verification & Trust Management.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class VerificationType(str, Enum):
    """Supported verification categories."""
    IDENTITY = "identity"
    PROFILE = "profile"
    CONTACT = "contact"
    ADDRESS = "address"
    SKILL = "skill"
    EXPERIENCE = "experience"


class VerificationStatus(str, Enum):
    """Verification workflow state lifecycle."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    RESUBMISSION_REQUIRED = "resubmission_required"


class TrustBadgeType(str, Enum):
    """Supported trust badge types."""
    VERIFIED_WORKER = "verified_worker"
    IDENTITY_VERIFIED = "identity_verified"
    EXPERIENCED_WORKER = "experienced_worker"
    TOP_RATED = "top_rated"
    FAST_RESPONDER = "fast_responder"
    TRUSTED_PROFESSIONAL = "trusted_professional"


# ---------------------------------------------------------------------------
# Verification DTOs
# ---------------------------------------------------------------------------

class VerificationSubmitRequest(BaseModel):
    """Worker request to submit verification for admin review."""
    verification_type: VerificationType
    document_ids: list[str] = Field(default_factory=list, description="IDs of uploaded verification documents")
    notes: str | None = Field(default=None, max_length=1000, description="Optional worker notes")
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationRead(BaseModel):
    """Full verification record response schema."""
    id: PyObjectId
    verification_id: str
    worker_id: str
    verification_type: VerificationType
    status: VerificationStatus
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewer_id: str | None = None
    review_notes: str | None = None
    document_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerificationStatusRead(BaseModel):
    """Overview summary of a worker's verification state across all types."""
    worker_id: str
    overall_status: VerificationStatus
    type_statuses: dict[str, VerificationStatus]
    approved_count: int
    pending_count: int
    earned_badges: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Document Management DTOs
# ---------------------------------------------------------------------------

class DocumentUploadResponse(BaseModel):
    """Response returned upon uploading a document to Cloudinary & MongoDB."""
    id: PyObjectId
    document_id: str
    worker_id: str
    verification_id: str | None = None
    document_type: str
    document_number: str | None = None
    secure_url: str
    public_id: str
    version: int
    status: VerificationStatus
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VerificationResubmitRequest(BaseModel):
    """Worker payload to resubmit a requested verification."""
    verification_id: str
    new_document_ids: list[str] | None = Field(default=None, description="Updated document IDs")
    notes: str | None = Field(default=None, max_length=1000)


# ---------------------------------------------------------------------------
# Admin Review DTOs
# ---------------------------------------------------------------------------

class VerificationReviewRequest(BaseModel):
    """Admin payload to move verification request to 'under_review'."""
    verification_id: str
    review_notes: str | None = Field(default=None, max_length=1000)


class VerificationApprovalRequest(BaseModel):
    """Admin payload to approve a verification request."""
    verification_id: str
    review_notes: str | None = Field(default=None, max_length=1000)
    grant_badges: list[TrustBadgeType] | None = Field(default=None, description="Optional trust badges to grant")


class VerificationRejectionRequest(BaseModel):
    """Admin payload to reject or request resubmission."""
    verification_id: str
    review_notes: str = Field(..., max_length=1000, description="Reason for rejection or resubmission request")
    request_resubmission: bool = Field(default=False, description="If True, status becomes resubmission_required instead of rejected")


# ---------------------------------------------------------------------------
# Trust Badge DTOs
# ---------------------------------------------------------------------------

class TrustBadgeRead(BaseModel):
    """Badge response DTO."""
    id: PyObjectId
    badge_id: str
    worker_id: str
    badge_type: TrustBadgeType
    badge_name: str
    description: str
    icon_url: str | None = None
    granted_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TrustBadgeRule(BaseModel):
    """Rule definition for configurable trust badges."""
    badge_type: TrustBadgeType
    badge_name: str
    description: str
    required_verification_type: VerificationType | None = None
    trust_score_bonus: float = 5.0
