"""
Beanie document models for Security Monitoring & Audit Center database collections.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid
from beanie import Document, Indexed
from pydantic import Field

from app.security_center.schemas import (
    PlatformHealthStatus,
    SecurityAlertPriority,
    SecurityAlertStatus,
    SecurityEventType,
)
from app.trust.schemas import RiskLevel


def default_utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a string representation of UUID4."""
    return str(uuid.uuid4())


class SecurityEvent(Document):
    """
    Centralized security event log entry document.

    Collection: security_events
    """
    event_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str | None, Indexed()] = None
    event_type: Annotated[SecurityEventType, Indexed()]
    severity: Annotated[RiskLevel, Indexed()] = RiskLevel.LOW
    description: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "security_events"
        indexes = [
            "user_id",
            "event_type",
            "severity",
            "created_at",
        ]


class SecurityAlert(Document):
    """
    Administrative security alert document.

    Collection: security_alerts
    """
    alert_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    title: str
    description: str
    priority: Annotated[SecurityAlertPriority, Indexed()] = SecurityAlertPriority.MEDIUM
    status: Annotated[SecurityAlertStatus, Indexed()] = SecurityAlertStatus.OPEN
    user_id: str | None = None
    assigned_admin_id: str | None = None
    triggered_by: str = "system"
    resolution_notes: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)
    resolved_at: datetime | None = None

    class Settings:
        name = "security_alerts"
        indexes = [
            "status",
            "priority",
            "created_at",
        ]


class LoginHistory(Document):
    """
    Authentication session and login history document.

    Collection: login_history
    """
    session_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    user_id: Annotated[str, Indexed()]
    is_success: Annotated[bool, Indexed()] = True
    ip_address: str = "127.0.0.1"
    user_agent: str = "unknown"
    device_info: dict[str, Any] = Field(default_factory=dict)
    failure_reason: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "login_history"
        indexes = [
            "user_id",
            "is_success",
            "created_at",
        ]


class APIMonitoringRecord(Document):
    """
    API traffic, latency, and response code metric record document.

    Collection: api_monitoring
    """
    record_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=generate_uuid)
    endpoint: Annotated[str, Indexed()]
    http_method: str
    status_code: Annotated[int, Indexed()]
    response_time_ms: float
    user_id: str | None = None
    ip_address: str | None = None
    created_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "api_monitoring"
        indexes = [
            "endpoint",
            "status_code",
            "created_at",
        ]


class SecurityDashboardCache(Document):
    """
    Cached security health metrics and dashboard summary.

    Collection: security_dashboard_cache
    """
    cache_id: Annotated[str, Indexed(unique=True)] = "latest"
    overall_health: PlatformHealthStatus = PlatformHealthStatus.HEALTHY
    active_alerts_count: dict[str, int] = Field(default_factory=dict)
    failed_logins_24h: int = 0
    api_error_rate: float = 0.0
    api_avg_latency_ms: float = 0.0
    updated_at: datetime = Field(default_factory=default_utc_now)

    class Settings:
        name = "security_dashboard_cache"
        indexes = [
            "cache_id",
        ]
