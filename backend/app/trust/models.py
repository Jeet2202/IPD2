"""
Beanie document models for Trust & Safety Infrastructure database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.trust.schemas import (
    AuditEventType,
    RiskEventType,
    RiskLevel,
    ReviewStatus,
    TrustLevel,
    TrustVerificationStatus,
)
from app.utils.enums import UserRole


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class TrustProfile(Document):
    """
    User trust profile state for customers and workers.

    Collection: trust_profiles
    """
    user_id: Annotated[str, Indexed(unique=True)]
    role: UserRole
    trust_score: float = Field(default=75.0, ge=0.0, le=100.0)
    trust_level: TrustLevel = TrustLevel.STANDARD
    verification_status: TrustVerificationStatus = TrustVerificationStatus.UNVERIFIED
    risk_level: RiskLevel = RiskLevel.LOW
    review_status: ReviewStatus = ReviewStatus.CLEAR
    safety_flags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "trust_profiles"
        indexes = [
            "user_id",
            "trust_level",
            "risk_level",
            "role",
        ]


class TrustPolicy(Document):
    """
    Configurable safety and risk policies/thresholds.

    Collection: trust_policies
    """
    policy_key: Annotated[str, Indexed(unique=True)]
    name: str
    category: Annotated[str, Indexed()]
    rules: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    version: int = 1
    created_at: datetime = Field(default_factory=default_utc_now)
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "trust_policies"
        indexes = [
            "policy_key",
            "category",
            "is_active",
        ]


class RiskEvent(Document):
    """
    Recorded risk management event log.

    Collection: risk_events
    """
    event_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    event_type: RiskEventType
    severity: RiskLevel = RiskLevel.LOW
    description: str
    source: str = "system"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "risk_events"
        indexes = [
            "user_id",
            "event_type",
            "severity",
            "created_at",
        ]


class TrustAuditLog(Document):
    """
    Immutable audit records for trust and safety events.

    Collection: audit_logs
    """
    event_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    event_type: AuditEventType
    description: str
    timestamp: datetime = Field(default_factory=default_utc_now)
    actor: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "audit_logs"
        indexes = [
            "user_id",
            "event_type",
            "timestamp",
        ]


class SafetyFlag(Document):
    """
    Safety flag instance attached to a user.

    Collection: safety_flags
    """
    flag_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    flag_type: str
    reason: str
    severity: RiskLevel = RiskLevel.MEDIUM
    status: str = "active"  # "active", "resolved"
    created_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "safety_flags"
        indexes = [
            "user_id",
            "status",
            "severity",
        ]


class VerificationHistory(Document):
    """
    Historical verification records.

    Collection: verification_history
    """
    history_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    verification_type: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "verification_history"
        indexes = [
            "user_id",
            "verification_type",
            "timestamp",
        ]
