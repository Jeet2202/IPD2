"""
Pydantic v2 schemas and Enums for Reporting, Moderation & Dispute Resolution.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.trust.schemas import RiskLevel

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ReportTargetType(str, Enum):
    """Platform entities that can be reported."""
    WORKER = "worker"
    CUSTOMER = "customer"
    BOOKING = "booking"
    QUOTATION = "quotation"
    REVIEW = "review"
    PROFILE = "profile"
    UPLOADED_CONTENT = "uploaded_content"


class ReportCategory(str, Enum):
    """Categories of reports and policy violations."""
    SPAM = "spam"
    FAKE_PROFILE = "fake_profile"
    POOR_SERVICE = "poor_service"
    ABUSE = "abuse"
    HARASSMENT = "harassment"
    FRAUD = "fraud"
    INAPPROPRIATE_BEHAVIOUR = "inappropriate_behaviour"
    POLICY_VIOLATION = "policy_violation"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Lifecycle state of reports."""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    INVESTIGATION = "investigation"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    CLOSED = "closed"


class DisputeType(str, Enum):
    """Formal dispute categories."""
    CUSTOMER_VS_WORKER = "customer_vs_worker"
    WORKER_VS_CUSTOMER = "worker_vs_customer"
    WORKER_VS_PLATFORM = "worker_vs_platform"
    CUSTOMER_VS_PLATFORM = "customer_vs_platform"


class DisputeStatus(str, Enum):
    """Lifecycle state of disputes."""
    SUBMITTED = "submitted"
    UNDER_INVESTIGATION = "under_investigation"
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class AdministrativeAction(str, Enum):
    """Enforceable administrative actions."""
    WARNING = "warning"
    TRUST_SCORE_ADJUSTMENT = "trust_score_adjustment"
    TEMPORARY_RESTRICTION = "temporary_restriction"
    ACCOUNT_SUSPENSION = "account_suspension"
    PERMANENT_BAN = "permanent_ban"
    REPORT_DISMISSAL = "report_dismissal"


# ---------------------------------------------------------------------------
# Evidence DTOs
# ---------------------------------------------------------------------------

class EvidenceUploadResponse(BaseModel):
    """DTO for evidence file metadata."""
    evidence_id: str
    case_id: str
    uploader_id: str
    file_name: str
    file_type: str
    secure_url: str
    public_id: str
    description: str | None = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Report DTOs
# ---------------------------------------------------------------------------

class ReportCreate(BaseModel):
    """Payload to file a new platform report."""
    target_type: ReportTargetType
    target_id: str
    category: ReportCategory
    description: str = Field(..., max_length=2000, description="Detailed explanation of the issue")


class ReportUpdate(BaseModel):
    """Payload to update report state or resolution."""
    status: ReportStatus | None = None
    resolution_action: AdministrativeAction | None = None
    resolution_notes: str | None = Field(default=None, max_length=2000)


class ReportRead(BaseModel):
    """Stored report schema."""
    id: PyObjectId
    report_id: str
    reporter_id: str
    target_type: ReportTargetType
    target_id: str
    category: ReportCategory
    description: str
    status: ReportStatus
    severity: RiskLevel | None = None
    assigned_moderator_id: str | None = None
    resolution_action: str | None = None
    resolution_notes: str | None = None
    evidence_files: list[EvidenceUploadResponse] = Field(default_factory=list)
    case_notes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Moderation DTOs
# ---------------------------------------------------------------------------

class ModerationReviewRequest(BaseModel):
    """Payload for moderator review of a report or case."""
    report_id: str
    severity: RiskLevel
    assigned_moderator_id: str | None = None
    recommended_action: AdministrativeAction | None = None
    notes: str | None = Field(default=None, max_length=1000)


class ModerationEscalateRequest(BaseModel):
    """Payload to escalate a report or dispute to senior admin."""
    case_id: str = Field(..., description="report_id or dispute_id")
    reason: str = Field(..., max_length=1000)


# ---------------------------------------------------------------------------
# Dispute DTOs
# ---------------------------------------------------------------------------

class DisputeCreate(BaseModel):
    """Payload to open a dispute case."""
    dispute_type: DisputeType
    respondent_id: str = Field(..., description="Target party ID (Customer, Worker, or Platform)")
    booking_id: str | None = None
    reason: str = Field(..., max_length=3000, description="Detailed dispute statement")


class DisputeResolveRequest(BaseModel):
    """Payload for final resolution of a dispute case."""
    dispute_id: str
    resolution_decision: str = Field(..., max_length=2000, description="Final decision statement")
    administrative_action: AdministrativeAction | None = None
    target_user_id: str | None = Field(default=None, description="User subject to administrative action")
    trust_score_delta: float = Field(default=0.0, description="Trust score adjustment delta e.g. -10.0 or +5.0")


class DisputeRead(BaseModel):
    """Stored dispute schema."""
    id: PyObjectId
    dispute_id: str
    dispute_type: DisputeType
    booking_id: str | None = None
    initiator_id: str
    respondent_id: str
    reason: str
    status: DisputeStatus
    assigned_moderator_id: str | None = None
    resolution_decision: str | None = None
    administrative_action: str | None = None
    trust_score_delta: float = 0.0
    evidence_files: list[EvidenceUploadResponse] = Field(default_factory=list)
    case_notes: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CaseNoteCreate(BaseModel):
    """Payload to log a timeline note on a case."""
    case_id: str = Field(..., description="report_id or dispute_id")
    note_text: str = Field(..., max_length=2000)
    is_internal_only: bool = Field(default=False, description="True if only visible to moderators/admins")
