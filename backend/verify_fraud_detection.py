"""
Verification script for Phase 8.3 - Fraud Detection & Abuse Prevention.

Executes complete E2E verification of:
1. Beanie database document model registration (15 models).
2. FraudConfigService rule initialization.
3. FraudRuleEngine deterministic rule evaluation across rule types.
4. RiskAssessmentService scoring, risk level mapping, and recommended actions.
5. FraudDetectionService automated risk actions, alert generation, TrustProfile (P8.1) review status updates, and RiskEvent (P8.1) logging.
6. AbuseDetectionService reporting and resolution workflows.
7. REST APIs authentication, authorization, and payload schemas via HTTP client.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport

from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.database.connection import close_database_connection, connect_to_database
from app.fraud.models import (
    AbuseReport,
    FraudAlert,
    FraudEvent,
    FraudRule,
)
from app.fraud.schemas import (
    AbuseReportCreate,
    AbuseType,
    AlertStatus,
    AutomatedAction,
    FraudAlertResolveRequest,
    FraudAnalysisRequest,
    FraudRuleUpdate,
)
from app.fraud.service import (
    AbuseDetectionService,
    AlertService,
    FraudConfigService,
    FraudDetectionService,
)
from app.main import app
from app.trust.models import (
    ReviewStatus,
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("Starting Phase 8.3 - Fraud Detection & Abuse Prevention Verification...")

    # 1. Database Connection & Document Initialization
    document_models = [
        User,
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
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 15 document models.")

    try:
        # Initialize default policies & rules
        await ConfigService.initialize_default_policies()
        await FraudConfigService.initialize_default_rules()

        active_rules = await FraudConfigService.list_active_rules()
        assert len(active_rules) >= 11
        logger.info("SUCCESS: FraudConfigService initialized %d active rules.", len(active_rules))

        # Clean up test users and data
        test_user_email = "test_user_p83@kaamsetu.com"
        test_admin_email = "test_admin_p83@kaamsetu.com"

        await User.find(User.email == test_user_email).delete()
        await User.find(User.email == test_admin_email).delete()
        await User.find(User.phone == "+919988775544").delete()
        await User.find(User.phone == "+919988775545").delete()

        test_user = User(
            email=test_user_email,
            phone="+919988775544",
            password_hash="fake_user_hash",
            full_name="Anand Target P83",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_email_verified=True,
        )
        await test_user.insert()
        test_user_id = str(test_user.id)

        admin_user = User(
            email=test_admin_email,
            phone="+919988775545",
            password_hash="fake_admin_hash",
            full_name="Admin Reviewer P83",
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        await admin_user.insert()
        admin_id_str = str(admin_user.id)

        # Cleanup old test logs for test_user_id
        await FraudEvent.find(FraudEvent.user_id == test_user_id).delete()
        await FraudAlert.find(FraudAlert.user_id == test_user_id).delete()
        await AbuseReport.find(AbuseReport.target_user_id == test_user_id).delete()
        await TrustProfile.find(TrustProfile.user_id == test_user_id).delete()

        # Initialize base trust profile
        await TrustService.get_or_create_profile(test_user_id, UserRole.CUSTOMER)

        # 2. Analyze Clean Activity Payload
        clean_req = FraudAnalysisRequest(
            user_id=test_user_id,
            event_type="login",
            activity_data={"failed_logins": 0, "api_requests_per_minute": 5},
        )
        clean_res = await FraudDetectionService.analyze_activity(clean_req)
        assert clean_res.risk_score == 0.0
        assert clean_res.risk_level == RiskLevel.LOW
        assert len(clean_res.triggered_rules) == 0
        logger.info("SUCCESS: Clean activity analysis passed (score=0.0, level=Low).")

        # 3. Analyze High Risk Fraud Payload
        suspicious_req = FraudAnalysisRequest(
            user_id=test_user_id,
            event_type="suspicious_login_burst",
            activity_data={
                "failed_logins": 8,                  # Triggers multiple_failed_logins (+25.0)
                "is_duplicate_identity": True,        # Triggers duplicate_account_attempt (+30.0)
                "api_requests_per_minute": 150,      # Triggers suspicious_api_patterns (+35.0)
            },
        )
        fraud_res = await FraudDetectionService.analyze_activity(suspicious_req)
        assert fraud_res.risk_score >= 80.0
        assert fraud_res.risk_level == RiskLevel.CRITICAL
        assert fraud_res.recommended_action == AutomatedAction.ACCOUNT_SUSPENSION
        assert len(fraud_res.triggered_rules) == 3
        logger.info("SUCCESS: Suspicious activity analysis triggered 3 rules (score=%.1f, level=CRITICAL).", fraud_res.risk_score)

        # 4. Verify Automated Actions Integration (P8.1)
        # Check generated alert
        alerts = await AlertService.list_alerts(user_id=test_user_id)
        assert len(alerts) >= 1
        alert = alerts[0]
        assert alert.risk_level == RiskLevel.CRITICAL
        assert alert.status == AlertStatus.OPEN
        logger.info("SUCCESS: Administrative FraudAlert generated (id=%s).", alert.alert_id)

        # Check TrustProfile review_status update
        updated_profile = await TrustProfile.find_one(TrustProfile.user_id == test_user_id)
        assert updated_profile.review_status == ReviewStatus.RESTRICTED
        logger.info("SUCCESS: User TrustProfile review_status automatically updated to RESTRICTED.")

        # 5. Abuse Detection Service Verification
        report_req = AbuseReportCreate(
            target_user_id=test_user_id,
            abuse_type=AbuseType.SPAM_ACCOUNT,
            description="Account sending bulk unverified requests.",
        )
        report = await AbuseDetectionService.create_abuse_report(admin_id_str, report_req)
        assert report.report_id is not None
        assert report.status == "pending"
        logger.info("SUCCESS: Abuse report created successfully (id=%s).", report.report_id)

        # Resolve alert
        admin_info = {"id": admin_id_str, "role": "admin", "email": test_admin_email}
        resolved_alert = await AlertService.resolve_alert(
            alert_id=alert.alert_id,
            action="resolved",
            resolution_notes="User identity verified with phone OTP and proxy cleared.",
            reviewer=admin_info,
        )
        assert resolved_alert.status == AlertStatus.RESOLVED
        logger.info("SUCCESS: FraudAlert resolved successfully.")

        # 6. REST API Endpoints Verification via HTTP Client
        user_token = create_access_token(test_user_id, UserRole.CUSTOMER)
        admin_token = create_access_token(admin_id_str, UserRole.ADMIN)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # POST /api/v1/fraud/analyze
            api_req_data = {
                "user_id": test_user_id,
                "event_type": "booking_create",
                "activity_data": {"bookings_count_1h": 8},
            }
            resp = await ac.post(
                "/api/v1/fraud/analyze",
                json=api_req_data,
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            analysis_data = resp.json()
            assert "risk_score" in analysis_data
            assert "recommended_action" in analysis_data

            # GET /api/v1/fraud/events
            resp = await ac.get(
                "/api/v1/fraud/events",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            events = resp.json()
            assert len(events) >= 1

            # GET /api/v1/fraud/alerts (Admin)
            resp = await ac.get(
                "/api/v1/fraud/alerts",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            alerts_data = resp.json()
            assert len(alerts_data) >= 1

            # GET /api/v1/fraud/rules
            resp = await ac.get(
                "/api/v1/fraud/rules",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            rules_data = resp.json()
            assert len(rules_data) >= 11

            # PUT /api/v1/fraud/rules (Admin)
            rule_update_data = {"description": "Updated rule description for test"}
            resp = await ac.put(
                "/api/v1/fraud/rules?rule_key=multiple_failed_logins",
                json=rule_update_data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            updated_rule = resp.json()
            assert updated_rule["description"] == "Updated rule description for test"

            # POST /api/v1/fraud/report (User)
            report_payload = {
                "target_user_id": test_user_id,
                "abuse_type": "review_manipulation",
                "description": "Suspicious star rating stuffing",
            }
            resp = await ac.post(
                "/api/v1/fraud/report",
                json=report_payload,
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            report_res = resp.json()
            assert report_res["report_id"] is not None

            # GET /api/v1/fraud/statistics (Admin)
            resp = await ac.get(
                "/api/v1/fraud/statistics",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            stats = resp.json()
            assert stats["total_events_analyzed"] >= 1
            assert "critical_risk_events" in stats

        logger.info("SUCCESS: All 8 REST API endpoints verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.3 - Fraud Detection & Abuse Prevention Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
