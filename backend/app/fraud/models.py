"""
Beanie document models for Fraud Detection & Abuse Prevention database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.fraud.schemas import (
    AbuseType,
    AlertPriority,
    AlertStatus,
    FraudRuleType,
)
from app.trust.schemas import RiskLevel


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class FraudEvent(Document):
    """
    Recorded fraud detection analysis event log.

    Collection: fraud_events
    """
    event_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    event_type: Annotated[str, Indexed()]
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    risk_level: RiskLevel = RiskLevel.LOW
    risk_reason: str = "Normal user activity"
    triggered_rules: list[str] = Field(default_factory=list)
    recommended_action: str = "none"
    event_data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "fraud_events"
        indexes = [
            "user_id",
            "event_type",
            "risk_level",
            "created_at",
        ]


class FraudRule(Document):
    """
    Configurable rule definition for fraud detection.

    Collection: fraud_rules
    """
    rule_key: Annotated[str, Indexed(unique=True)]
    name: str
    description: str
    rule_type: FraudRuleType
    severity: RiskLevel = RiskLevel.MEDIUM
    score_impact: float = 20.0
    thresholds: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    version: int = 1
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "fraud_rules"
        indexes = [
            "rule_key",
            "rule_type",
            "is_active",
        ]


class FraudAlert(Document):
    """
    Administrative fraud and risk alert.

    Collection: fraud_alerts
    """
    alert_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    title: str
    description: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    priority: AlertPriority = AlertPriority.MEDIUM
    status: AlertStatus = AlertStatus.OPEN
    assigned_reviewer_id: str | None = None
    triggered_rules: list[str] = Field(default_factory=list)
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None

    class Settings:
        name = "fraud_alerts"
        indexes = [
            "user_id",
            "status",
            "priority",
            "created_at",
        ]


class AbuseReport(Document):
    """
    Report of user abuse, spam, or review manipulation.

    Collection: abuse_reports
    """
    report_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    reporter_id: Annotated[str, Indexed()]
    target_user_id: Annotated[str, Indexed()]
    abuse_type: AbuseType
    description: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"  # "pending", "investigating", "resolved", "dismissed"
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None

    class Settings:
        name = "abuse_reports"
        indexes = [
            "target_user_id",
            "abuse_type",
            "status",
            "created_at",
        ]
