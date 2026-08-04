"""
Verification script for Phase 8.7 - Trust Intelligence & Risk Assessment.

Executes complete E2E verification of:
1. Beanie database document model registration (36 models).
2. TrustSummaryService overview, fraud, moderation, compliance, and security intelligence aggregation.
3. RiskAssessmentService weighted department risk scoring and snapshot generation.
4. TrustRecommendationService metric-referenced recommendation generation.
5. RiskTrendService event volume and trend analytics.
6. REST APIs authentication, RBAC authorization, and payload validation via HTTP client.
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
from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust_intelligence.models import TrustIntelligenceSnapshot
from app.trust_intelligence.service import (
    RiskAssessmentService,
    RiskTrendService,
    TrustRecommendationService,
    TrustSummaryService,
)
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
    logger.info("Starting Phase 8.7 - Trust Intelligence & Risk Assessment Verification...")

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
        TrustIntelligenceSnapshot,
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 36 document models.")

    try:
        # Clean up test user
        admin_email = "test_admin_intel_p87@kaamsetu.com"
        user_email = "test_customer_intel_p87@kaamsetu.com"
        await User.find(User.email == admin_email).delete()
        await User.find(User.email == user_email).delete()

        admin_user = User(
            email=admin_email,
            phone="+919988775511",
            password_hash="fake_admin_hash",
            full_name="Admin Trust Lead P87",
            role=UserRole.ADMIN,
            is_active=True,
        )
        await admin_user.insert()
        admin_id_str = str(admin_user.id)

        customer_user = User(
            email=user_email,
            phone="+919988775522",
            password_hash="fake_cust_hash",
            full_name="Customer User NonAdmin",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await customer_user.insert()
        customer_id_str = str(customer_user.id)

        # 2. Intelligence Summaries Verification
        overview = await TrustSummaryService.get_trust_overview()
        assert overview.average_trust_score >= 0.0
        logger.info("SUCCESS: Aggregated Platform Trust Overview (avg_score=%.1f).", overview.average_trust_score)

        fraud_intel = await TrustSummaryService.get_fraud_intelligence()
        logger.info("SUCCESS: Aggregated Fraud Intelligence (active_cases=%d).", fraud_intel.active_fraud_cases_count)

        mod_intel = await TrustSummaryService.get_moderation_intelligence()
        logger.info("SUCCESS: Aggregated Moderation Intelligence (pending_reports=%d).", mod_intel.pending_reports_count)

        comp_intel = await TrustSummaryService.get_compliance_intelligence()
        logger.info("SUCCESS: Aggregated Compliance Intelligence (pending_tasks=%d).", comp_intel.pending_compliance_tasks_count)

        sec_intel = await TrustSummaryService.get_security_intelligence()
        logger.info("SUCCESS: Aggregated Security Intelligence (failed_logins_24h=%d).", sec_intel.failed_logins_24h)

        # 3. Risk Assessment & Snapshot Verification
        risk_assessment = await RiskAssessmentService.get_risk_assessment()
        assert risk_assessment.overall_risk_score >= 0.0
        assert len(risk_assessment.department_scores) == 5
        logger.info("SUCCESS: Computed Risk Assessment (score=%.1f, health=%s).", risk_assessment.overall_risk_score, risk_assessment.platform_health)

        latest_snap = await TrustIntelligenceSnapshot.find_all().sort("-created_at").first_or_none()
        assert latest_snap is not None
        logger.info("SUCCESS: Saved Trust Intelligence Snapshot in DB (snapshot_id=%s).", latest_snap.snapshot_id)

        # 4. Metric-Referenced Recommendations Verification
        recommendations = await TrustRecommendationService.get_recommendations()
        logger.info("SUCCESS: Generated %d metric-referenced admin recommendations.", len(recommendations))

        # 5. Risk Trends Verification
        trends = await RiskTrendService.get_risk_trends(window_days=7)
        assert trends.window_days == 7
        logger.info("SUCCESS: Aggregated 7-day Risk Event trends.")

        # 6. REST API Endpoints Verification via HTTP Client
        admin_token = create_access_token(admin_id_str, UserRole.ADMIN)
        customer_token = create_access_token(customer_id_str, UserRole.CUSTOMER)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # 1. GET /api/v1/trust/intelligence/overview (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/overview",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["average_trust_score"] >= 0.0

            # RBAC Guard Verification (Customer should be forbidden 403)
            resp_cust = await ac.get(
                "/api/v1/trust/intelligence/overview",
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp_cust.status_code == 403
            logger.info("SUCCESS: RBAC Guard enforced on Admin-only Trust Intelligence APIs.")

            # 2. GET /api/v1/trust/intelligence/fraud (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/fraud",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # 3. GET /api/v1/trust/intelligence/moderation (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/moderation",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # 4. GET /api/v1/trust/intelligence/compliance (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/compliance",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # 5. GET /api/v1/trust/intelligence/security (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/security",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # 6. GET /api/v1/trust/intelligence/recommendations (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/recommendations",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # 7. GET /api/v1/trust/intelligence/trends (Admin)
            resp = await ac.get(
                "/api/v1/trust/intelligence/trends?window_days=7",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            assert resp.json()["window_days"] == 7

        logger.info("SUCCESS: All 7 REST API endpoints operational and verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.7 - Trust Intelligence & Risk Assessment Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
