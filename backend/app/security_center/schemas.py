"""
Pydantic v2 schemas and Enums for Security Monitoring & Audit Center.
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

class SecurityEventType(str, Enum):
    """Centralized security event categorizations."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    MULTIPLE_FAILED_LOGINS = "multiple_failed_logins"
    PASSWORD_RESET = "password_reset"
    ROLE_CHANGE = "role_change"
    PERMISSION_CHANGE = "permission_change"
    PROFILE_CHANGE = "profile_change"
    TRUST_SCORE_CHANGE = "trust_score_change"
    FRAUD_ALERT_RECEIVED = "fraud_alert_received"
    MODERATION_ACTION = "moderation_action"
    ADMIN_ACTION = "admin_action"
    API_AUTH_FAILURE = "api_auth_failure"
    TOKEN_EXPIRY = "token_expiry"
    INVALID_TOKEN_USAGE = "invalid_token_usage"


class SecurityAlertPriority(str, Enum):
    """Urgency levels for security alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityAlertStatus(str, Enum):
    """Lifecycle state of security alerts."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class PlatformHealthStatus(str, Enum):
    """Platform health status evaluation."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Security Event DTOs
# ---------------------------------------------------------------------------

class SecurityEventCreate(BaseModel):
    """Payload to log a security event."""
    user_id: str | None = None
    event_type: SecurityEventType
    severity: RiskLevel = RiskLevel.LOW
    description: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SecurityEventRead(BaseModel):
    """Stored security event schema."""
    id: PyObjectId
    event_id: str
    user_id: str | None = None
    event_type: SecurityEventType
    severity: RiskLevel
    description: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Authentication Monitoring DTOs
# ---------------------------------------------------------------------------

class LoginHistoryRead(BaseModel):
    """Stored authentication login history schema."""
    id: PyObjectId
    session_id: str
    user_id: str
    is_success: bool
    ip_address: str
    user_agent: str
    device_info: dict[str, Any] = Field(default_factory=dict)
    failure_reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# API Traffic & Health DTOs
# ---------------------------------------------------------------------------

class APIMonitoringRecordCreate(BaseModel):
    """Payload to record an API invocation metric."""
    endpoint: str
    http_method: str
    status_code: int
    response_time_ms: float
    user_id: str | None = None
    ip_address: str | None = None


class APIHealthRead(BaseModel):
    """Aggregated API traffic and latency metrics DTO."""
    total_requests_24h: int
    avg_response_time_ms: float
    error_rate_percentage: float
    unauthorized_401_403_count: int
    server_error_5xx_count: int
    rate_limit_429_count: int
    status: PlatformHealthStatus
    generated_at: datetime


# ---------------------------------------------------------------------------
# Security Alert DTOs
# ---------------------------------------------------------------------------

class SecurityAlertRead(BaseModel):
    """Stored security alert schema."""
    id: PyObjectId
    alert_id: str
    title: str
    description: str
    priority: SecurityAlertPriority
    status: SecurityAlertStatus
    user_id: str | None = None
    assigned_admin_id: str | None = None
    triggered_by: str
    resolution_notes: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SecurityAlertAcknowledgeRequest(BaseModel):
    """Payload to acknowledge or resolve a security alert."""
    alert_id: str
    action: str = Field(..., description="'acknowledged', 'resolved', or 'dismissed'")
    notes: str = Field(..., max_length=1000)


# ---------------------------------------------------------------------------
# Security Dashboard & Statistics DTOs
# ---------------------------------------------------------------------------

class SecurityDashboardRead(BaseModel):
    """Centralized Security Dashboard overview metrics."""
    overall_health: PlatformHealthStatus
    active_alerts: dict[str, int] = Field(default_factory=dict)
    failed_logins_24h: int
    api_health: APIHealthRead
    recent_security_events: list[SecurityEventRead] = Field(default_factory=list)
    administrative_actions_count_24h: int
    generated_at: datetime


class SecurityStatisticsRead(BaseModel):
    """High-level platform security statistics summary."""
    total_events_logged: int
    total_logins_24h: int
    successful_logins_24h: int
    failed_logins_24h: int
    active_alerts_count: int
    resolved_alerts_count: int
    api_requests_24h: int
    generated_at: datetime
