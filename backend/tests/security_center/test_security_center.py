"""
Unit tests for Security Monitoring & Audit Center services.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.security_center.models import (
    APIMonitoringRecord,
    LoginHistory,
    SecurityAlert,
    SecurityEvent,
)
from app.security_center.schemas import (
    APIMonitoringRecordCreate,
    PlatformHealthStatus,
    SecurityAlertAcknowledgeRequest,
    SecurityAlertPriority,
    SecurityAlertStatus,
    SecurityEventCreate,
    SecurityEventType,
)
from app.security_center.service import (
    APIMonitoringService,
    AuthMonitoringService,
    SecurityAlertService,
    SecurityDashboardService,
    SecurityEventService,
)
from app.trust.schemas import RiskLevel


@pytest.mark.asyncio
async def test_log_security_event():
    """Verify security event logging saves event and records audit log."""
    event_in = SecurityEventCreate(
        user_id="usr_sec_100",
        event_type=SecurityEventType.PASSWORD_RESET,
        severity=RiskLevel.MEDIUM,
        description="Password reset requested",
        ip_address="1.2.3.4",
    )

    fake_doc = SecurityEvent.model_construct(
        event_id="ev_100",
        user_id="usr_sec_100",
        event_type=SecurityEventType.PASSWORD_RESET,
        severity=RiskLevel.MEDIUM,
        description="Password reset requested",
        created_at=MagicMock(),
    )

    with patch("app.security_center.repository.SecurityEventRepository.create_event", new_callable=AsyncMock, return_value=fake_doc), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit:

        res = await SecurityEventService.log_security_event(event_in)
        assert res.event_id == "ev_100"
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_record_login_attempt_triggers_alert_on_burst():
    """Verify 5 failed login attempts in 1 hour triggers a SecurityAlert."""
    user_id = "usr_sec_200"

    fake_login = LoginHistory.model_construct(session_id="sess_1", user_id=user_id, is_success=False)

    with patch("app.security_center.repository.LoginHistoryRepository.create_login", new_callable=AsyncMock, return_value=fake_login), \
         patch("app.security_center.service.SecurityEventService.log_security_event", new_callable=AsyncMock), \
         patch("app.security_center.repository.LoginHistoryRepository.count_recent_logins", new_callable=AsyncMock, return_value=5), \
         patch("app.security_center.service.SecurityAlertService.generate_alert", new_callable=AsyncMock) as mock_gen_alert:

        res = await AuthMonitoringService.record_login_attempt(user_id=user_id, is_success=False, failure_reason="Wrong password")
        assert res.session_id == "sess_1"
        mock_gen_alert.assert_called_once()


@pytest.mark.asyncio
async def test_api_health_evaluation():
    """Verify API health status transitions based on error rate percentage."""
    health_data = {
        "total_requests_24h": 100,
        "avg_response_time_ms": 45.5,
        "error_rate_percentage": 12.0,  # >10% => CRITICAL
        "unauthorized_401_403_count": 5,
        "server_error_5xx_count": 7,
        "rate_limit_429_count": 0,
    }

    with patch("app.security_center.repository.APIMonitoringRepository.get_health_metrics", new_callable=AsyncMock, return_value=health_data):
        health = await APIMonitoringService.get_api_health(hours=24)
        assert health.status == PlatformHealthStatus.CRITICAL
        assert health.total_requests_24h == 100


@pytest.mark.asyncio
async def test_acknowledge_security_alert():
    """Verify administrative alert acknowledgment."""
    fake_alert = SecurityAlert.model_construct(
        alert_id="alt_555",
        title="Test Alert",
        status=SecurityAlertStatus.ACKNOWLEDGED,
        priority=SecurityAlertPriority.HIGH,
    )

    req = SecurityAlertAcknowledgeRequest(alert_id="alt_555", action="acknowledged", notes="Under investigation")
    admin_info = {"id": "admin_1", "role": "admin", "email": "admin@kaamsetu.com"}

    with patch("app.security_center.repository.SecurityAlertRepository.acknowledge_alert", new_callable=AsyncMock, return_value=fake_alert), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit:

        updated = await SecurityAlertService.acknowledge_alert(req, admin_info)
        assert updated.status == SecurityAlertStatus.ACKNOWLEDGED
        mock_audit.assert_called_once()
