from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from app.utils.enums import UserRole

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TrustLevel(str, Enum):
    """Trust levels based on score thresholds."""
    EXCELLENT = "Excellent"
    TRUSTED = "Trusted"
    STANDARD = "Standard"
    WATCHLIST = "Watchlist"
    HIGH_RISK = "High Risk"
    RESTRICTED = "Restricted"


class RiskLevel(str, Enum):
    """System-wide risk levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ReviewStatus(str, Enum):
    """Review and flag lifecycle state of a profile."""
    CLEAR = "clear"
    UNDER_REVIEW = "under_review"
    FLAGGED = "flagged"
    RESTRICTED = "restricted"


class TrustVerificationStatus(str, Enum):
    """Trust framework verification status."""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    PARTIALLY_VERIFIED = "partially_verified"
    FULLY_VERIFIED = "fully_verified"


class RiskEventType(str, Enum):
    """Supported risk event categorizations."""
    FAILED_VERIFICATION = "Failed Verification"
    SUSPICIOUS_ACTIVITY = "Suspicious Activity"
    MULTIPLE_LOGIN_ATTEMPTS = "Multiple Login Attempts"
    POLICY_VIOLATIONS = "Policy Violations"
    SAFETY_EVENTS = "Safety Events"
    MANUAL_REVIEWS = "Manual Reviews"


class AuditEventType(str, Enum):
    """Supported immutable audit log event types."""
    REGISTRATION = "Registration"
    LOGIN = "Login"
    LOGOUT = "Logout"
    PROFILE_UPDATES = "Profile Updates"
    VERIFICATION_CHANGES = "Verification Changes"
    TRUST_SCORE_CHANGES = "Trust Score Changes"
    ADMINISTRATIVE_ACTIONS = "Administrative Actions"
    POLICY_CHANGES = "Policy Changes"
    RISK_EVENTS = "Risk Events"


# ---------------------------------------------------------------------------
# Trust Profile Schemas
# ---------------------------------------------------------------------------

class TrustProfileBase(BaseModel):
    user_id: str
    role: UserRole
    trust_score: float = Field(default=75.0, ge=0.0, le=100.0)
    trust_level: TrustLevel = TrustLevel.STANDARD
    verification_status: TrustVerificationStatus = TrustVerificationStatus.UNVERIFIED
    risk_level: RiskLevel = RiskLevel.LOW
    review_status: ReviewStatus = ReviewStatus.CLEAR
    safety_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrustProfileRead(TrustProfileBase):
    id: PyObjectId
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrustProfileUpdate(BaseModel):
    trust_score: float | None = Field(default=None, ge=0.0, le=100.0)
    trust_level: TrustLevel | None = None
    verification_status: TrustVerificationStatus | None = None
    risk_level: RiskLevel | None = None
    review_status: ReviewStatus | None = None
    safety_flags: list[str] | None = None
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Trust Status Overview Schema
# ---------------------------------------------------------------------------

class TrustStatusRead(BaseModel):
    user_id: str
    role: UserRole
    trust_score: float
    trust_level: TrustLevel
    risk_level: RiskLevel
    review_status: ReviewStatus
    verification_status: TrustVerificationStatus
    active_flags_count: int
    is_restricted: bool
    last_updated: datetime


# ---------------------------------------------------------------------------
# Risk Event Schemas
# ---------------------------------------------------------------------------

class RiskEventCreate(BaseModel):
    user_id: str
    event_type: RiskEventType
    severity: RiskLevel = RiskLevel.LOW
    description: str
    source: str = "system"
    metadata: dict[str, Any] = Field(default_factory=dict)


class RiskEventRead(BaseModel):
    id: PyObjectId
    event_id: str
    user_id: str
    event_type: RiskEventType
    severity: RiskLevel
    description: str
    source: str
    metadata: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Audit Log Schemas
# ---------------------------------------------------------------------------

class AuditLogCreate(BaseModel):
    user_id: str
    event_type: AuditEventType
    description: str
    actor: dict[str, Any] = Field(..., description="Information about who performed the action")
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditLogRead(BaseModel):
    id: PyObjectId
    event_id: str
    user_id: str
    event_type: AuditEventType
    description: str
    timestamp: datetime
    actor: dict[str, Any]
    metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Policy Management Schemas
# ---------------------------------------------------------------------------

class TrustPolicyBase(BaseModel):
    policy_key: str
    name: str
    category: str = Field(..., description="Category like score_thresholds, risk_thresholds, escalation, restriction, review")
    rules: dict[str, Any]
    is_active: bool = True
    version: int = 1


class TrustPolicyCreate(TrustPolicyBase):
    pass


class TrustPolicyUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    rules: dict[str, Any] | None = None
    is_active: bool | None = None


class TrustPolicyRead(TrustPolicyBase):
    id: PyObjectId
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Safety Flag Schemas
# ---------------------------------------------------------------------------

class SafetyFlagCreate(BaseModel):
    user_id: str
    flag_type: str
    reason: str
    severity: RiskLevel = RiskLevel.MEDIUM
    metadata: dict[str, Any] = Field(default_factory=dict)


class SafetyFlagRead(BaseModel):
    id: PyObjectId
    flag_id: str
    user_id: str
    flag_type: str
    reason: str
    severity: RiskLevel
    status: str
    created_at: datetime
    resolved_at: datetime | None = None
    metadata: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Verification History Schemas
# ---------------------------------------------------------------------------

class VerificationHistoryCreate(BaseModel):
    user_id: str
    verification_type: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class VerificationHistoryRead(BaseModel):
    id: PyObjectId
    history_id: str
    user_id: str
    verification_type: str
    status: str
    details: dict[str, Any]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Review Action Schemas
# ---------------------------------------------------------------------------

class TrustReviewCreate(BaseModel):
    target_user_id: str
    action: str = Field(..., description="Action such as 'flag', 'clear', 'restrict', 'under_review'")
    reason: str
    new_risk_level: RiskLevel | None = None
    notes: str | None = None


class TrustReviewResponse(BaseModel):
    target_user_id: str
    action: str
    previous_review_status: ReviewStatus
    new_review_status: ReviewStatus
    previous_risk_level: RiskLevel
    new_risk_level: RiskLevel
    reviewed_at: datetime
    reviewer_id: str
