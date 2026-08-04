"""
Repositories for Security Monitoring & Audit Center following Clean Architecture & Repository Pattern.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from app.security_center.models import (
    APIMonitoringRecord,
    LoginHistory,
    SecurityAlert,
    SecurityDashboardCache,
    SecurityEvent,
)
from app.security_center.schemas import (
    SecurityAlertPriority,
    SecurityAlertStatus,
    SecurityEventType,
)
from app.trust.schemas import RiskLevel


class SecurityEventRepository:
    """Repository for managing SecurityEvent database operations."""

    @staticmethod
    async def create_event(data: dict[str, Any]) -> SecurityEvent:
        """Create and save a new SecurityEvent."""
        event = SecurityEvent(**data)
        await event.insert()
        return event

    @staticmethod
    async def list_events(
        user_id: str | None = None,
        event_type: SecurityEventType | None = None,
        severity: RiskLevel | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SecurityEvent]:
        """Query security events with optional filtering."""
        query: dict[str, Any] = {}
        if user_id:
            query["user_id"] = user_id
        if event_type:
            query["event_type"] = event_type
        if severity:
            query["severity"] = severity

        return (
            await SecurityEvent.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_total() -> int:
        """Count total logged security events."""
        return await SecurityEvent.find_all().count()

    @staticmethod
    async def count_events_24h(event_type: SecurityEventType | None = None) -> int:
        """Count security events in last 24 hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        query: dict[str, Any] = {"created_at": {"$gte": since}}
        if event_type:
            query["event_type"] = event_type
        return await SecurityEvent.find(query).count()


class SecurityAlertRepository:
    """Repository for managing SecurityAlert database operations."""

    @staticmethod
    async def get_by_id(alert_id: str) -> SecurityAlert | None:
        """Fetch alert by unique alert_id."""
        return await SecurityAlert.find_one(SecurityAlert.alert_id == alert_id)

    @staticmethod
    async def create_alert(data: dict[str, Any]) -> SecurityAlert:
        """Create and save a new SecurityAlert."""
        alert = SecurityAlert(**data)
        await alert.insert()
        return alert

    @staticmethod
    async def list_alerts(
        status: SecurityAlertStatus | None = None,
        priority: SecurityAlertPriority | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SecurityAlert]:
        """Query security alerts."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority

        return (
            await SecurityAlert.find(query)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def acknowledge_alert(
        alert_id: str,
        action: str,
        resolution_notes: str,
        admin_id: str,
    ) -> SecurityAlert | None:
        """Acknowledge or resolve an alert."""
        alert = await SecurityAlertRepository.get_by_id(alert_id)
        if not alert:
            return None

        if action.lower() == "acknowledged":
            alert.status = SecurityAlertStatus.ACKNOWLEDGED
        elif action.lower() == "resolved":
            alert.status = SecurityAlertStatus.RESOLVED
            alert.resolved_at = datetime.now(timezone.utc)
        else:
            alert.status = SecurityAlertStatus.DISMISSED
            alert.resolved_at = datetime.now(timezone.utc)

        alert.assigned_admin_id = admin_id
        alert.resolution_notes = resolution_notes

        await alert.save()
        return alert

    @staticmethod
    async def count_active_by_priority() -> dict[str, int]:
        """Count open security alerts grouped by priority."""
        open_alerts = await SecurityAlert.find(SecurityAlert.status == SecurityAlertStatus.OPEN).to_list()
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for a in open_alerts:
            p_val = a.priority.value if hasattr(a.priority, "value") else str(a.priority)
            counts[p_val.lower()] = counts.get(p_val.lower(), 0) + 1
        return counts


class LoginHistoryRepository:
    """Repository for managing LoginHistory database operations."""

    @staticmethod
    async def create_login(data: dict[str, Any]) -> LoginHistory:
        """Record an authentication login attempt."""
        entry = LoginHistory(**data)
        await entry.insert()
        return entry

    @staticmethod
    async def list_by_user(user_id: str, skip: int = 0, limit: int = 50) -> list[LoginHistory]:
        """Fetch login history for a user."""
        return (
            await LoginHistory.find(LoginHistory.user_id == user_id)
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_recent_logins(user_id: str | None = None, is_success: bool = True, hours: int = 24) -> int:
        """Count login attempts in last N hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        query: dict[str, Any] = {"is_success": is_success, "created_at": {"$gte": since}}
        if user_id:
            query["user_id"] = user_id
        return await LoginHistory.find(query).count()


class APIMonitoringRepository:
    """Repository for managing APIMonitoringRecord database operations."""

    @staticmethod
    async def create_record(data: dict[str, Any]) -> APIMonitoringRecord:
        """Save API request metric."""
        rec = APIMonitoringRecord(**data)
        await rec.insert()
        return rec

    @staticmethod
    async def get_health_metrics(hours: int = 24) -> dict[str, Any]:
        """Compute aggregated API traffic and latency metrics for last N hours."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        records = await APIMonitoringRecord.find(APIMonitoringRecord.created_at >= since).to_list()

        total = len(records)
        if total == 0:
            return {
                "total_requests_24h": 0,
                "avg_response_time_ms": 0.0,
                "error_rate_percentage": 0.0,
                "unauthorized_401_403_count": 0,
                "server_error_5xx_count": 0,
                "rate_limit_429_count": 0,
            }

        avg_latency = sum(r.response_time_ms for r in records) / total
        unauthorized = sum(1 for r in records if r.status_code in [401, 403])
        server_errors = sum(1 for r in records if r.status_code >= 500)
        rate_limits = sum(1 for r in records if r.status_code == 429)
        total_errors = sum(1 for r in records if r.status_code >= 400)
        error_rate = (total_errors / total) * 100.0

        return {
            "total_requests_24h": total,
            "avg_response_time_ms": round(avg_latency, 2),
            "error_rate_percentage": round(error_rate, 2),
            "unauthorized_401_403_count": unauthorized,
            "server_error_5xx_count": server_errors,
            "rate_limit_429_count": rate_limits,
        }


class SecurityDashboardCacheRepository:
    """Repository for managing SecurityDashboardCache database operations."""

    @staticmethod
    async def get_latest() -> SecurityDashboardCache | None:
        """Fetch latest security dashboard cache."""
        return await SecurityDashboardCache.find_one(SecurityDashboardCache.cache_id == "latest")

    @staticmethod
    async def save_cache(data: dict[str, Any]) -> SecurityDashboardCache:
        """Update or insert dashboard cache."""
        existing = await SecurityDashboardCacheRepository.get_latest()
        now = datetime.now(timezone.utc)
        data["updated_at"] = now

        if existing:
            for k, v in data.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            await existing.save()
            return existing

        cache = SecurityDashboardCache(**data)
        await cache.insert()
        return cache
