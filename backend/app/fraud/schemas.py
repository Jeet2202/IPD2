"""
Pydantic v2 schemas and Enums for Fraud Detection & Abuse Prevention.
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

class FraudRuleType(str, Enum):
    """Supported rule categories for fraud detection."""
    MULTIPLE_FAILED_LOGINS = "multiple_failed_logins"
    DUPLICATE_ACCOUNT_ATTEMPT = "duplicate_account_attempt"
    RAPID_BOOKING_CREATION = "rapid_booking_creation"
    EXCESSIVE_CANCELLATION = "excessive_cancellation"
    SUSPICIOUS_QUOTATION_ACTIVITY = "suspicious_quotation_activity"
    REPEATED_VERIFICATION_FAILURES = "repeated_verification_failures"
    SPAM_BEHAVIOUR = "spam_behaviour"
    REVIEW_ABUSE = "review_abuse"
    EXCESSIVE_PROFILE_UPDATES = "excessive_profile_updates"
    UNUSUAL_LOGIN_LOCATION = "unusual_login_location"
    SUSPICIOUS_API_PATTERNS = "suspicious_api_patterns"


class AbuseType(str, Enum):
    """Supported categories of platform abuse."""
    SPAM_ACCOUNT = "spam_account"
    FAKE_BOOKING = "fake_booking"
    FAKE_WORKER_PROFILE = "fake_worker_profile"
    REVIEW_MANIPULATION = "review_manipulation"
    EXCESSIVE_MESSAGING = "excessive_messaging"
    REPEATED_POLICY_VIOLATIONS = "repeated_policy_violations"


class AlertStatus(str, Enum):
    """Lifecycle state of administrative fraud alerts."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertPriority(str, Enum):
    """Urgency level of fraud alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutomatedAction(str, Enum):
    """Automated administrative action recommendations."""
    WARNING = "warning"
    MANUAL_REVIEW = "manual_review"
    TEMPORARY_RESTRICTION = "temporary_restriction"
    ACCOUNT_SUSPENSION = "account_suspension"
    PERMANENT_BAN = "permanent_ban"


# ---------------------------------------------------------------------------
# Fraud Analysis DTOs
# ---------------------------------------------------------------------------

class FraudAnalysisRequest(BaseModel):
    """Payload sent to analyze user activity/events against fraud rules."""
    user_id: str
    event_type: str = Field(..., description="Context event e.g. login, booking_create, review_post, verification_upload")
    activity_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Event context metrics e.g. failed_logins_1h, bookings_count_1h, cancellation_rate, is_unusual_location, etc.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class TriggeredRuleDetail(BaseModel):
    """Detail of a single fraud rule match."""
    rule_key: str
    name: str
    rule_type: FraudRuleType
    severity: RiskLevel
    score_impact: float
    reason: str


class FraudAnalysisResponse(BaseModel):
    """Result response of fraud analysis evaluation."""
    user_id: str
    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    risk_reason: str
    triggered_rules: list[TriggeredRuleDetail] = Field(default_factory=list)
    recommended_action: AutomatedAction
    event_id: str
    analyzed_at: datetime


class FraudEventRead(BaseModel):
    """Stored fraud analysis log event DTO."""
    id: PyObjectId
    event_id: str
    user_id: str
    event_type: str
    risk_score: float
    risk_level: RiskLevel
    risk_reason: str
    triggered_rules: list[str] = Field(default_factory=list)
    recommended_action: str
    event_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Fraud Rule Management DTOs
# ---------------------------------------------------------------------------

class FraudRuleRead(BaseModel):
    """Fraud detection rule DTO."""
    id: PyObjectId
    rule_key: str
    name: str
    description: str
    rule_type: FraudRuleType
    severity: RiskLevel
    score_impact: float
    thresholds: dict[str, Any]
    is_active: bool
    version: int

    model_config = ConfigDict(from_attributes=True)


class FraudRuleCreate(BaseModel):
    """Payload to define a new fraud rule."""
    rule_key: str
    name: str
    description: str
    rule_type: FraudRuleType
    severity: RiskLevel = RiskLevel.MEDIUM
    score_impact: float = 20.0
    thresholds: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class FraudRuleUpdate(BaseModel):
    """Payload to update an existing fraud rule."""
    name: str | None = None
    description: str | None = None
    severity: RiskLevel | None = None
    score_impact: float | None = None
    thresholds: dict[str, Any] | None = None
    is_active: bool | None = None


# ---------------------------------------------------------------------------
# Fraud Alert & Abuse DTOs
# ---------------------------------------------------------------------------

class FraudAlertRead(BaseModel):
    """Fraud alert schema."""
    id: PyObjectId
    alert_id: str
    user_id: str
    title: str
    description: str
    risk_level: RiskLevel
    priority: AlertPriority
    status: AlertStatus
    assigned_reviewer_id: str | None = None
    triggered_rules: list[str] = Field(default_factory=list)
    resolution_notes: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FraudAlertResolveRequest(BaseModel):
    """Payload to resolve or dismiss an alert or report."""
    target_id: str = Field(..., description="alert_id or report_id")
    action: str = Field(..., description="'resolved' or 'dismissed'")
    notes: str = Field(..., max_length=1000, description="Resolution rationale")


class AbuseReportCreate(BaseModel):
    """Payload to submit an abuse report."""
    target_user_id: str
    abuse_type: AbuseType
    description: str = Field(..., max_length=2000)
    evidence: dict[str, Any] = Field(default_factory=dict)


class AbuseReportRead(BaseModel):
    """Abuse report schema."""
    id: PyObjectId
    report_id: str
    reporter_id: str
    target_user_id: str
    abuse_type: AbuseType
    description: str
    evidence: dict[str, Any]
    status: str
    resolution_notes: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FraudStatisticsRead(BaseModel):
    """Platform fraud & abuse statistics overview."""
    total_events_analyzed: int
    critical_risk_events: int
    high_risk_events: int
    medium_risk_events: int
    open_alerts_count: int
    resolved_alerts_count: int
    pending_abuse_reports: int
    generated_at: datetime
