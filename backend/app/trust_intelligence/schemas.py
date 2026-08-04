"""
Pydantic v2 schemas and Enums for Trust Intelligence & Risk Assessment.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RecommendationPriority(str, Enum):
    """Priority levels for metric-referenced recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DepartmentCategory(str, Enum):
    """Department domains for risk assessment."""
    FRAUD = "fraud"
    MODERATION = "moderation"
    SECURITY = "security"
    VERIFICATION = "verification"
    COMPLIANCE = "compliance"


class RiskLevelGrade(str, Enum):
    """Risk scoring severity grades."""
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Domain Intelligence DTOs
# ---------------------------------------------------------------------------

class TrustOverviewRead(BaseModel):
    """Platform trust score distribution & worker verification overview."""
    average_trust_score: float
    trust_distribution: dict[str, int] = Field(default_factory=dict)
    total_workers: int
    verified_workers_count: int
    pending_verifications_count: int
    restricted_accounts_count: int
    high_risk_users_count: int
    generated_at: datetime


class FraudIntelligenceRead(BaseModel):
    """Fraud intelligence and rule trigger statistics."""
    active_fraud_cases_count: int
    high_risk_accounts_count: int
    rule_trigger_stats: dict[str, int] = Field(default_factory=dict)
    fraud_resolution_rate_percentage: float
    generated_at: datetime


class ModerationIntelligenceRead(BaseModel):
    """Moderation workload and dispute resolution statistics."""
    pending_reports_count: int
    escalated_reports_count: int
    open_disputes_count: int
    avg_resolution_time_hours: float
    generated_at: datetime


class ComplianceIntelligenceRead(BaseModel):
    """Privacy, consents, and data export request intelligence."""
    privacy_requests_count: int
    data_export_requests_count: int
    pending_compliance_tasks_count: int
    consent_granted_percentages: dict[str, float] = Field(default_factory=dict)
    generated_at: datetime


class SecurityIntelligenceRead(BaseModel):
    """Security monitoring and authentication metrics."""
    failed_logins_24h: int
    api_auth_failures_24h: int
    active_security_alerts_count: int
    critical_security_events_24h: int
    generated_at: datetime


# ---------------------------------------------------------------------------
# Risk Assessment DTOs
# ---------------------------------------------------------------------------

class DepartmentRiskScore(BaseModel):
    """Department-level risk score and primary driver."""
    department: DepartmentCategory
    risk_score: float
    grade: RiskLevelGrade
    primary_driver: str


class RiskAssessmentRead(BaseModel):
    """Overall platform risk assessment and health analysis."""
    overall_risk_score: float
    overall_grade: RiskLevelGrade
    department_scores: list[DepartmentRiskScore] = Field(default_factory=list)
    high_risk_areas: list[str] = Field(default_factory=list)
    platform_health: str
    generated_at: datetime


class MetricRecommendation(BaseModel):
    """Metric-referenced admin recommendation DTO."""
    recommendation_id: str
    title: str
    description: str
    department: DepartmentCategory
    priority: RecommendationPriority
    metric_citation: str
    suggested_action: str


class RiskTrendRead(BaseModel):
    """Historical risk event and score trend analytics."""
    window_days: int
    risk_events_by_category: dict[str, int] = Field(default_factory=dict)
    fraud_alerts_count_7d: int
    security_alerts_count_7d: int
    moderation_reports_count_7d: int
    generated_at: datetime
