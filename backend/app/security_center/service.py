"""
Domain services for Security Monitoring & Audit Center.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from app.core.exceptions import NotFoundException
from app.security_center.models import (
    APIMonitoringRecord,
    LoginHistory,
    SecurityAlert,
    SecurityDashboardCache,
    SecurityEvent,
)
from app.security_center.repository import (
    APIMonitoringRepository,
    LoginHistoryRepository,
    SecurityAlertRepository,
    SecurityDashboardCacheRepository,
    SecurityEventRepository,
)
from app.security_center.schemas import (
    APIHealthRead,
    APIMonitoringRecordCreate,
    PlatformHealthStatus,
    SecurityAlertAcknowledgeRequest,
    SecurityAlertPriority,
    SecurityAlertStatus,
    SecurityDashboardRead,
    SecurityEventCreate,
    SecurityEventRead,
    SecurityEventType,
    SecurityStatisticsRead,
)
from app.trust.schemas import AuditEventType, RiskLevel
from app.trust.service import AuditService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Security Event Service
# ---------------------------------------------------------------------------

class SecurityEventService:
    """Centralized security event recording and querying."""

    @staticmethod
    async def log_security_event(event_in: SecurityEventCreate) -> SecurityEvent:
        """Record a centralized security event in DB and audit trail."""
        user_id_str = str(event_in.user_id) if event_in.user_id else None

        event = await SecurityEventRepository.create_event({
            "user_id": user_id_str,
            "event_type": event_in.event_type,
            "severity": event_in.severity,
            "description": event_in.description,
            "ip_address": event_in.ip_address,
            "user_agent": event_in.user_agent,
            "metadata": event_in.metadata,
        })

        await AuditService.log_event(
            user_id=user_id_str or "system",
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Security Event [{event_in.event_type.value}]: {event_in.description}",
            actor={"id": user_id_str or "system", "role": "system"},
            metadata={"event_id": event.event_id, "severity": event_in.severity.value},
        )
        return event

    @staticmethod
    async def list_security_events(
        user_id: str | None = None,
        event_type: SecurityEventType | None = None,
        severity: RiskLevel | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SecurityEvent]:
        """List security events with optional filtering."""
        return await SecurityEventRepository.list_events(
            user_id=user_id, event_type=event_type, severity=severity, skip=skip, limit=limit
        )


# ---------------------------------------------------------------------------
# Authentication Monitoring Service
# ---------------------------------------------------------------------------

class AuthMonitoringService:
    """Monitors active sessions, login history, and authentication anomalies."""

    @staticmethod
    async def record_login_attempt(
        user_id: str,
        is_success: bool,
        ip_address: str = "127.0.0.1",
        user_agent: str = "unknown",
        failure_reason: str | None = None,
        device_info: dict[str, Any] | None = None,
    ) -> LoginHistory:
        """Record an authentication login attempt and monitor failed attempt bursts."""
        user_id_str = str(user_id)

        entry = await LoginHistoryRepository.create_login({
            "user_id": user_id_str,
            "is_success": is_success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_info": device_info or {},
            "failure_reason": failure_reason,
        })

        if is_success:
            await SecurityEventService.log_security_event(
                SecurityEventCreate(
                    user_id=user_id_str,
                    event_type=SecurityEventType.LOGIN_SUCCESS,
                    severity=RiskLevel.LOW,
                    description=f"Successful login from IP {ip_address}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
        else:
            await SecurityEventService.log_security_event(
                SecurityEventCreate(
                    user_id=user_id_str,
                    event_type=SecurityEventType.LOGIN_FAILURE,
                    severity=RiskLevel.MEDIUM,
                    description=f"Failed login attempt: {failure_reason or 'Invalid credentials'}",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )

            # Check if user has exceeded 5 failed logins in last hour
            recent_failures = await LoginHistoryRepository.count_recent_logins(
                user_id=user_id_str, is_success=False, hours=1
            )
            if recent_failures >= 5:
                await SecurityEventService.log_security_event(
                    SecurityEventCreate(
                        user_id=user_id_str,
                        event_type=SecurityEventType.MULTIPLE_FAILED_LOGINS,
                        severity=RiskLevel.HIGH,
                        description=f"Multiple failed logins detected: {recent_failures} attempts in 1 hour.",
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                )

                await SecurityAlertService.generate_alert(
                    title="Excessive Failed Login Attempts Detected",
                    description=f"User {user_id_str} recorded {recent_failures} failed login attempts in 1 hour.",
                    priority=SecurityAlertPriority.HIGH,
                    user_id=user_id_str,
                    triggered_by="auth_monitoring_service",
                )

        return entry

    @staticmethod
    async def get_user_login_history(
        user_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[LoginHistory]:
        """Fetch login history for user."""
        return await LoginHistoryRepository.list_by_user(str(user_id), skip=skip, limit=limit)


# ---------------------------------------------------------------------------
# API Monitoring Service
# ---------------------------------------------------------------------------

class APIMonitoringService:
    """Tracks API endpoint traffic, latency, and error rate health."""

    @staticmethod
    async def record_api_metric(metric_in: APIMonitoringRecordCreate) -> APIMonitoringRecord:
        """Save API request performance & status metric."""
        rec = await APIMonitoringRepository.create_record(metric_in.model_dump())

        if metric_in.status_code in [401, 403]:
            await SecurityEventService.log_security_event(
                SecurityEventCreate(
                    user_id=metric_in.user_id,
                    event_type=SecurityEventType.API_AUTH_FAILURE,
                    severity=RiskLevel.MEDIUM,
                    description=f"API authentication failure ({metric_in.status_code}) on endpoint {metric_in.endpoint}",
                    ip_address=metric_in.ip_address,
                )
            )

        return rec

    @staticmethod
    async def get_api_health(hours: int = 24) -> APIHealthRead:
        """Compute API traffic and error metrics for last N hours."""
        metrics = await APIMonitoringRepository.get_health_metrics(hours=hours)

        error_rate = metrics["error_rate_percentage"]
        server_errors = metrics["server_error_5xx_count"]

        if error_rate >= 10.0 or server_errors >= 10:
            health_status = PlatformHealthStatus.CRITICAL
        elif error_rate >= 5.0 or server_errors >= 3:
            health_status = PlatformHealthStatus.WARNING
        else:
            health_status = PlatformHealthStatus.HEALTHY

        return APIHealthRead(
            total_requests_24h=metrics["total_requests_24h"],
            avg_response_time_ms=metrics["avg_response_time_ms"],
            error_rate_percentage=metrics["error_rate_percentage"],
            unauthorized_401_403_count=metrics["unauthorized_401_403_count"],
            server_error_5xx_count=metrics["server_error_5xx_count"],
            rate_limit_429_count=metrics["rate_limit_429_count"],
            status=health_status,
            generated_at=datetime.now(timezone.utc),
        )


# ---------------------------------------------------------------------------
# Security Alert Service
# ---------------------------------------------------------------------------

class SecurityAlertService:
    """Generates and manages administrative security alerts."""

    @staticmethod
    async def generate_alert(
        title: str,
        description: str,
        priority: SecurityAlertPriority = SecurityAlertPriority.MEDIUM,
        user_id: str | None = None,
        triggered_by: str = "system",
    ) -> SecurityAlert:
        """Create and save an administrative security alert."""
        alert = await SecurityAlertRepository.create_alert({
            "title": title,
            "description": description,
            "priority": priority,
            "status": SecurityAlertStatus.OPEN,
            "user_id": str(user_id) if user_id else None,
            "triggered_by": triggered_by,
        })

        logger.warning("Security Alert generated: alert_id=%s, priority=%s, title='%s'", alert.alert_id, priority.value, title)
        return alert

    @staticmethod
    async def list_alerts(
        status: SecurityAlertStatus | None = None,
        priority: SecurityAlertPriority | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SecurityAlert]:
        """List administrative security alerts."""
        return await SecurityAlertRepository.list_alerts(
            status=status, priority=priority, skip=skip, limit=limit
        )

    @staticmethod
    async def acknowledge_alert(
        req: SecurityAlertAcknowledgeRequest,
        admin: dict[str, Any],
    ) -> SecurityAlert | None:
        """Acknowledge or resolve a security alert."""
        alert = await SecurityAlertRepository.acknowledge_alert(
            alert_id=req.alert_id,
            action=req.action,
            resolution_notes=req.notes,
            admin_id=admin["id"],
        )
        if not alert:
            raise NotFoundException(f"Security alert '{req.alert_id}' not found.")

        await AuditService.log_event(
            user_id=admin["id"],
            event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
            description=f"Security alert [{req.alert_id}] marked as '{alert.status.value}'",
            actor=admin,
            metadata={"alert_id": req.alert_id, "notes": req.notes},
        )
        return alert


# ---------------------------------------------------------------------------
# Security Dashboard Service
# ---------------------------------------------------------------------------

class SecurityDashboardService:
    """Aggregates backend platform security metrics and dashboard status."""

    @staticmethod
    async def get_security_dashboard() -> SecurityDashboardRead:
        """Compute aggregated security dashboard status."""
        active_alert_counts = await SecurityAlertRepository.count_active_by_priority()
        failed_logins_24h = await LoginHistoryRepository.count_recent_logins(is_success=False, hours=24)
        api_health = await APIMonitoringService.get_api_health(hours=24)
        recent_events = await SecurityEventRepository.list_events(limit=10)
        admin_actions_24h = await SecurityEventRepository.count_events_24h(SecurityEventType.ADMIN_ACTION)

        crit_count = active_alert_counts.get("critical", 0)
        high_count = active_alert_counts.get("high", 0)

        if crit_count > 0 or api_health.status == PlatformHealthStatus.CRITICAL:
            overall_health = PlatformHealthStatus.CRITICAL
        elif high_count > 0 or api_health.status == PlatformHealthStatus.WARNING:
            overall_health = PlatformHealthStatus.WARNING
        else:
            overall_health = PlatformHealthStatus.HEALTHY

        recent_dtos = [SecurityEventRead.model_validate(e) for e in recent_events]
        now = datetime.now(timezone.utc)

        # Cache calculation
        await SecurityDashboardCacheRepository.save_cache({
            "cache_id": "latest",
            "overall_health": overall_health,
            "active_alerts_count": active_alert_counts,
            "failed_logins_24h": failed_logins_24h,
            "api_error_rate": api_health.error_rate_percentage,
            "api_avg_latency_ms": api_health.avg_response_time_ms,
            "updated_at": now,
        })

        return SecurityDashboardRead(
            overall_health=overall_health,
            active_alerts=active_alert_counts,
            failed_logins_24h=failed_logins_24h,
            api_health=api_health,
            recent_security_events=recent_dtos,
            administrative_actions_count_24h=admin_actions_24h,
            generated_at=now,
        )

    @staticmethod
    async def get_security_statistics() -> SecurityStatisticsRead:
        """Compute high-level security statistics summary."""
        total_logged = await SecurityEventRepository.count_total()
        succ_logins_24h = await LoginHistoryRepository.count_recent_logins(is_success=True, hours=24)
        failed_logins_24h = await LoginHistoryRepository.count_recent_logins(is_success=False, hours=24)
        open_alerts = await SecurityAlertRepository.list_alerts(status=SecurityAlertStatus.OPEN)
        resolved_alerts = await SecurityAlertRepository.list_alerts(status=SecurityAlertStatus.RESOLVED)
        api_metrics = await APIMonitoringRepository.get_health_metrics(hours=24)

        return SecurityStatisticsRead(
            total_events_logged=total_logged,
            total_logins_24h=succ_logins_24h + failed_logins_24h,
            successful_logins_24h=succ_logins_24h,
            failed_logins_24h=failed_logins_24h,
            active_alerts_count=len(open_alerts),
            resolved_alerts_count=len(resolved_alerts),
            api_requests_24h=api_metrics["total_requests_24h"],
            generated_at=datetime.now(timezone.utc),
        )
