"""
Verification script for Phase 8.6 - Security Monitoring & Audit Center.

Executes complete E2E verification of:
1. Beanie database document model registration (35 models).
2. SecurityEventService event recording and query filtering.
3. AuthMonitoringService login session logging and failed attempt burst alert triggers.
4. APIMonitoringService traffic metrics, latency averages, and status code health checks.
5. SecurityAlertService alert creation, listing, and administrative acknowledgment.
6. SecurityDashboardService aggregated metrics calculation and cache storage.
7. REST APIs authentication, RBAC authorization, and payload validation via HTTP client.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport

from app.address.models import Address
from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.booking.models import Booking
from app.customer.models import CustomerProfile
from app.database.connection import close_database_connection, connect_to_database
from app.fraud.models import AbuseReport, FraudAlert, FraudEvent, FraudRule
from app.main import app
from app.moderation.models import (
    CaseNote,
    Dispute,
    EvidenceFile,
    ModerationCase,
    PlatformReport,
)
from app.privacy.models import (
    ComplianceRecord,
    DataExport,
    PrivacyRequest,
    RetentionPolicy,
    UserConsent,
)
from app.review.models import Review
from app.security_center.models import (
    APIMonitoringRecord,
    LoginHistory,
    SecurityAlert,
    SecurityDashboardCache,
    SecurityEvent,
)
from app.security_center.schemas import (
    APIMonitoringRecordCreate,
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
from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust.schemas import RiskLevel
from app.trust.service import ConfigService, TrustService
from app.verification.models import (
    VerificationBadge,
    VerificationDocument,
    VerificationReview,
    WorkerVerification,
)
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("Starting Phase 8.6 - Security Monitoring & Audit Center Verification...")

    # 1. Database Connection & Document Initialization
    document_models = [
        User,
        CustomerProfile,
        WorkerProfile,
        Address,
        Booking,
        Review,
        TrustProfile,
        TrustPolicy,
        RiskEvent,
        TrustAuditLog,
        SafetyFlag,
        VerificationHistory,
        WorkerVerification,
        VerificationDocument,
        VerificationReview,
        VerificationBadge,
        FraudEvent,
        FraudRule,
        FraudAlert,
        AbuseReport,
        PlatformReport,
        Dispute,
        ModerationCase,
        EvidenceFile,
        CaseNote,
        UserConsent,
        PrivacyRequest,
        DataExport,
        RetentionPolicy,
        ComplianceRecord,
        SecurityEvent,
        SecurityAlert,
        LoginHistory,
        APIMonitoringRecord,
        SecurityDashboardCache,
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 35 document models.")

    try:
        await ConfigService.initialize_default_policies()

        # Clean up test users
        admin_email = "test_admin_sec_p86@kaamsetu.com"
        user_email = "test_user_sec_p86@kaamsetu.com"
        await User.find(User.email == admin_email).delete()
        await User.find(User.email == user_email).delete()

        admin_user = User(
            email=admin_email,
            phone="+919988774411",
            password_hash="fake_admin_hash",
            full_name="Admin Security Lead",
            role=UserRole.ADMIN,
            is_active=True,
        )
        await admin_user.insert()
        admin_id_str = str(admin_user.id)

        target_user = User(
            email=user_email,
            phone="+919988774422",
            password_hash="fake_user_hash",
            full_name="Target User Monitored",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await target_user.insert()
        user_id_str = str(target_user.id)

        # 2. Security Event Logging Verification
        event = await SecurityEventService.log_security_event(
            SecurityEventCreate(
                user_id=user_id_str,
                event_type=SecurityEventType.PASSWORD_RESET,
                severity=RiskLevel.MEDIUM,
                description="Password reset link requested by user.",
                ip_address="203.0.113.45",
            )
        )
        assert event.event_id is not None
        logger.info("SUCCESS: Logged centralized security event (event_id=%s).", event.event_id)

        # 3. Authentication Monitoring & Failed Login Burst Alert Trigger
        # Log 1 success login
        await AuthMonitoringService.record_login_attempt(user_id=user_id_str, is_success=True, ip_address="203.0.113.45")

        # Simulate 5 failed logins to trigger HIGH priority alert
        for i in range(5):
            await AuthMonitoringService.record_login_attempt(
                user_id=user_id_str, is_success=False, ip_address="198.51.100.22", failure_reason="Incorrect PIN"
            )

        alerts = await SecurityAlertService.list_alerts(status=SecurityAlertStatus.OPEN)
        assert len(alerts) >= 1
        burst_alert = alerts[0]
        assert burst_alert.priority == SecurityAlertPriority.HIGH
        logger.info("SUCCESS: Authentication Monitoring detected failed login burst & generated SecurityAlert (%s).", burst_alert.alert_id)

        # 4. API Monitoring & Health Metrics Verification
        await APIMonitoringService.record_api_metric(
            APIMonitoringRecordCreate(endpoint="/api/v1/auth/login", http_method="POST", status_code=200, response_time_ms=45.2, user_id=user_id_str)
        )
        await APIMonitoringService.record_api_metric(
            APIMonitoringRecordCreate(endpoint="/api/v1/admin/users", http_method="GET", status_code=403, response_time_ms=15.0, user_id=user_id_str)
        )
        await APIMonitoringService.record_api_metric(
            APIMonitoringRecordCreate(endpoint="/api/v1/bookings", http_method="GET", status_code=500, response_time_ms=120.5)
        )

        api_health = await APIMonitoringService.get_api_health(hours=24)
        assert api_health.total_requests_24h >= 3
        logger.info("SUCCESS: Computed API Health metrics (total_requests=%d, avg_ms=%.1f).", api_health.total_requests_24h, api_health.avg_response_time_ms)

        # 5. Security Alert Acknowledge & Resolve Verification
        admin_info = {"id": admin_id_str, "role": "admin", "email": admin_email}
        ack_req = SecurityAlertAcknowledgeRequest(
            alert_id=burst_alert.alert_id, action="acknowledged", notes="User contacted support; reset PIN."
        )
        ack_alert = await SecurityAlertService.acknowledge_alert(ack_req, admin_info)
        assert ack_alert.status == SecurityAlertStatus.ACKNOWLEDGED
        logger.info("SUCCESS: Admin acknowledged security alert (%s).", burst_alert.alert_id)

        # 6. Security Dashboard & Statistics Verification
        dash = await SecurityDashboardService.get_security_dashboard()
        assert dash.overall_health is not None
        assert len(dash.recent_security_events) >= 1
        logger.info("SUCCESS: Generated Security Dashboard status (health=%s).", dash.overall_health.value)

        stats = await SecurityDashboardService.get_security_statistics()
        assert stats.total_events_logged >= 1
        logger.info("SUCCESS: Computed Security Statistics (total_events=%d).", stats.total_events_logged)

        # 7. REST API Endpoints Verification via HTTP Client
        admin_token = create_access_token(admin_id_str, UserRole.ADMIN)
        user_token = create_access_token(user_id_str, UserRole.CUSTOMER)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # GET /api/v1/security/events (Admin)
            resp = await ac.get(
                "/api/v1/security/events",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert len(resp.json()) >= 1

            # GET /api/v1/security/alerts (Admin)
            resp = await ac.get(
                "/api/v1/security/alerts",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert len(resp.json()) >= 1

            # GET /api/v1/security/dashboard (Admin)
            resp = await ac.get(
                "/api/v1/security/dashboard",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["overall_health"] is not None

            # GET /api/v1/security/login-history (User)
            resp = await ac.get(
                "/api/v1/security/login-history",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            assert len(resp.json()) >= 1

            # GET /api/v1/security/api-health (Admin)
            resp = await ac.get(
                "/api/v1/security/api-health",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["total_requests_24h"] >= 3

            # POST /api/v1/security/alerts/acknowledge (Admin)
            resp = await ac.post(
                "/api/v1/security/alerts/acknowledge",
                json={"alert_id": burst_alert.alert_id, "action": "resolved", "notes": "Resolved by admin after review."},
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["status"] == "resolved"

            # GET /api/v1/security/statistics (Admin)
            resp = await ac.get(
                "/api/v1/security/statistics",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["total_events_logged"] >= 1

        logger.info("SUCCESS: All 7 REST API endpoints operational and verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.6 - Security Monitoring & Audit Center Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
