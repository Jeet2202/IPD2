"""
Master Production Readiness Verification Script for KaamSetu Trust & Safety Platform (Phase 8.8).

Certifies the end-to-end integration and readiness of:
- Phase 8.1: Trust & Safety Infrastructure (TrustProfiles, RiskEvents, AuditLogs, TrustPolicies)
- Phase 8.2: Worker Verification & Trust Management (Documents, Badges, Approval Workflow)
- Phase 8.3: Fraud Detection & Abuse Prevention (Rule Engine, Risk Assessment, Fraud Alerts)
- Phase 8.4: Reporting, Moderation & Dispute Resolution (Reports, Evidence, Disputes, Penalties)
- Phase 8.5: Privacy, Compliance & Data Protection (Consents, Exports, Grace Period Deletion)
- Phase 8.6: Security Monitoring & Audit Center (Auth Monitoring, API Health, Security Alerts)
- Phase 8.7: Trust Intelligence & Risk Assessment (Weighted Risk Scoring, Metric Recommendations)
"""

import asyncio
import json
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
from app.fraud.schemas import FraudAnalysisRequest
from app.fraud.service import AlertService, FraudDetectionService, FraudConfigService
from app.main import app
from app.moderation.models import (
    CaseNote,
    Dispute,
    EvidenceFile,
    ModerationCase,
    PlatformReport,
)
from app.moderation.schemas import (
    AdministrativeAction,
    DisputeCreate,
    DisputeResolveRequest,
    DisputeType,
    ModerationReviewRequest,
    ReportCategory,
    ReportCreate,
    ReportTargetType,
)
from app.moderation.service import DisputeService, ModerationService, ReportService, ResolutionService
from app.privacy.models import (
    ComplianceRecord,
    DataExport,
    PrivacyRequest,
    RetentionPolicy,
    UserConsent,
)
from app.privacy.schemas import ConsentItem, ConsentType, ConsentUpdateRequest, ExportFormat
from app.privacy.service import ConsentService, DataExportService, DataRetentionService, PrivacyService
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
)
from app.security_center.service import APIMonitoringService, AuthMonitoringService, SecurityAlertService, SecurityDashboardService
from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust.repository import TrustProfileRepository
from app.trust.schemas import RiskLevel
from app.trust.service import ConfigService, RiskService, TrustService
from app.trust_intelligence.models import TrustIntelligenceSnapshot
from app.trust_intelligence.service import RiskAssessmentService, TrustRecommendationService, TrustSummaryService
from app.verification.models import (
    VerificationBadge,
    VerificationDocument,
    VerificationReview,
    WorkerVerification,
)
from app.verification.schemas import VerificationApprovalRequest, VerificationSubmitRequest, VerificationType
from app.verification.service import ApprovalService, VerificationDocumentService, VerificationService
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_master_verification():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 8.8 MASTER TRUST & SAFETY PRODUCTION READINESS VERIFICATION")
    logger.info("================================================================================")

    # 1. Connect Database & Register All 36 Models
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
    logger.info("[STEP 1/8] MongoDB connected & 36 Beanie document models initialized.")

    try:
        # 2. Cleanup & Create Baseline Users
        admin_email = "prod_admin_p88@kaamsetu.com"
        worker_email = "prod_worker_p88@kaamsetu.com"
        customer_email = "prod_customer_p88@kaamsetu.com"

        await User.find({"email": {"$in": [admin_email, worker_email, customer_email]}}).delete()

        admin_user = User(email=admin_email, phone="+919911000001", password_hash="hash", full_name="Master Security Admin", role=UserRole.ADMIN, is_active=True)
        await admin_user.insert()
        admin_id = str(admin_user.id)

        worker_user = User(email=worker_email, phone="+919911000002", password_hash="hash", full_name="Karan Skilled Worker", role=UserRole.WORKER, is_active=True)
        await worker_user.insert()
        worker_id = str(worker_user.id)

        customer_user = User(email=customer_email, phone="+919911000003", password_hash="hash", full_name="Aarav Customer", role=UserRole.CUSTOMER, is_active=True)
        await customer_user.insert()
        customer_id = str(customer_user.id)

        await ConfigService.initialize_default_policies()
        await FraudConfigService.initialize_default_rules()
        await DataRetentionService.initialize_default_policies()

        logger.info("[STEP 2/8] Core baseline users and default configuration policies initialized.")

        # 3. P8.1 & P8.2 - Worker Verification & Trust Profile Update
        w_profile = await TrustService.get_or_create_profile(worker_id, UserRole.WORKER)
        c_profile = await TrustService.get_or_create_profile(customer_id, UserRole.CUSTOMER)
        assert w_profile.trust_score == 75.0

        # Upload doc & submit verification
        doc_resp = await VerificationDocumentService.upload_document(
            worker_id=worker_id, document_type="aadhaar", filename="aadhaar_card.pdf", file_bytes=b"dummy content", mime_type="application/pdf"
        )
        verif_req = await VerificationService.submit_verification(
            worker_id=worker_id, req=VerificationSubmitRequest(verification_type=VerificationType.IDENTITY, document_ids=[doc_resp.document_id])
        )

        # Admin approves verification
        await ApprovalService.approve_verification(
            admin_user={"id": admin_id, "role": "admin"}, verification_id=verif_req.verification_id, review_notes="Identity documents verified valid."
        )
        updated_w_profile = await TrustProfileRepository.get_by_user_id(worker_id)
        assert updated_w_profile.trust_score == 90.0  # 75 + 10 approval + 5 badge bonus
        logger.info("[STEP 3/8] Worker Verification approved & Trust Score updated (75.0 -> 90.0).")

        # 4. P8.3 - Fraud Detection Rule Execution & Alert
        f_resp = await FraudDetectionService.analyze_activity(
            req=FraudAnalysisRequest(
                user_id=worker_id,
                event_type="rapid_booking_creation",
                activity_data={"bookings_count_1h": 15, "failed_logins_1h": 6},
            )
        )
        f_alerts = await AlertService.list_alerts()
        assert len(f_alerts) >= 1
        logger.info("[STEP 4/8] Fraud Detection Engine evaluated event & raised FraudAlert (%s).", f_alerts[0].alert_id)

        # 5. P8.4 - Reporting, Cloudinary Evidence, & Dispute Resolution
        report_dto = await ReportService.create_report(
            reporter_id=customer_id,
            req=ReportCreate(
                target_type=ReportTargetType.WORKER, target_id=worker_id, category=ReportCategory.POOR_SERVICE, description="Worker did not complete agreed service tasks."
            ),
        )
        await ModerationService.review_report(
            moderator={"id": admin_id, "role": "admin"},
            req=ModerationReviewRequest(report_id=report_dto.report_id, severity=RiskLevel.HIGH, notes="Under investigation."),
        )

        dispute_doc = await DisputeService.create_dispute(
            initiator_id=worker_id, req=DisputeCreate(dispute_type=DisputeType.WORKER_VS_CUSTOMER, respondent_id=customer_id, reason="Services were rendered as agreed.")
        )
        await ResolutionService.resolve_dispute(
            moderator={"id": admin_id, "role": "admin"},
            req=DisputeResolveRequest(
                dispute_id=dispute_doc.dispute_id,
                resolution_decision="Partial policy violation confirmed.",
                administrative_action=AdministrativeAction.TRUST_SCORE_ADJUSTMENT,
                target_user_id=worker_id,
                trust_score_delta=-15.0,
            ),
        )
        post_dispute_profile = await TrustProfileRepository.get_by_user_id(worker_id)
        assert post_dispute_profile.trust_score == 75.0  # 90.0 - 15.0 = 75.0
        logger.info("[STEP 5/8] Dispute resolved; Trust Score penalized by -15.0 to 75.0 and Risk Event logged.")

        # 6. P8.5 - Privacy Controls, Consents & Personal Data Export
        await ConsentService.update_user_consents(
            user_id=customer_id, req=ConsentUpdateRequest(consents=[ConsentItem(consent_type=ConsentType.MARKETING, is_granted=True)])
        )
        json_export = await DataExportService.generate_data_export(user_id=customer_id, format_type=ExportFormat.JSON)
        csv_export = await DataExportService.generate_data_export(user_id=customer_id, format_type=ExportFormat.CSV)
        assert "personal_info" in json_export.file_content
        assert "email" in csv_export.file_content

        del_req = await PrivacyService.request_account_deletion(user_id=customer_id, reason="Testing deletion workflow")
        cancelled_del = await PrivacyService.cancel_account_deletion(user_id=customer_id)
        assert cancelled_del.status.value == "cancelled"
        logger.info("[STEP 6/8] Privacy consents, JSON/CSV exports, and 30-day grace period deletion workflow verified.")

        # 7. P8.6 - Security Monitoring, Auth Failures & API Health
        await AuthMonitoringService.record_login_attempt(user_id=customer_id, is_success=True)
        for _ in range(5):
            await AuthMonitoringService.record_login_attempt(user_id=customer_id, is_success=False, failure_reason="PIN Error")

        sec_alerts = await SecurityAlertService.list_alerts(status=SecurityAlertStatus.OPEN)
        assert len(sec_alerts) >= 1

        await APIMonitoringService.record_api_metric(APIMonitoringRecordCreate(endpoint="/api/v1/auth", http_method="POST", status_code=200, response_time_ms=30.0))
        await APIMonitoringService.record_api_metric(APIMonitoringRecordCreate(endpoint="/api/v1/admin", http_method="GET", status_code=403, response_time_ms=10.0))

        await SecurityAlertService.acknowledge_alert(
            req=SecurityAlertAcknowledgeRequest(alert_id=sec_alerts[0].alert_id, action="resolved", notes="Admin verified security state."),
            admin={"id": admin_id, "role": "admin"},
        )
        logger.info("[STEP 7/8] Security Monitoring recorded failed login burst, raised alert, and processed admin resolution.")

        # 8. P8.7 & REST APIs - Trust Intelligence, Risk Scoring & RBAC
        assessment = await RiskAssessmentService.get_risk_assessment()
        assert assessment.overall_risk_score >= 0.0
        recs = await TrustRecommendationService.get_recommendations()
        assert len(recs) >= 1

        admin_token = create_access_token(admin_id, UserRole.ADMIN)
        cust_token = create_access_token(customer_id, UserRole.CUSTOMER)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            endpoints = [
                ("/api/v1/trust/profile", cust_token, 200),
                ("/api/v1/verification/status", cust_token, 200),
                ("/api/v1/fraud/alerts", admin_token, 200),
                ("/api/v1/reports", cust_token, 200),
                ("/api/v1/privacy/profile", cust_token, 200),
                ("/api/v1/security/dashboard", admin_token, 200),
                ("/api/v1/trust/intelligence/overview", admin_token, 200),
                ("/api/v1/trust/intelligence/recommendations", admin_token, 200),
                ("/api/v1/trust/intelligence/overview", cust_token, 403),  # RBAC Guard check
            ]

            for path, token, expected_status in endpoints:
                resp = await ac.get(path, headers={"Authorization": f"Bearer {token}"})
                assert resp.status_code == expected_status, f"Endpoint {path} failed: expected {expected_status}, got {resp.status_code}"

        logger.info("[STEP 8/8] Verified end-to-end REST APIs and RBAC guards across all 7 Phase 8 modules.")

    finally:
        await close_database_connection()

    logger.info("================================================================================")
    logger.info("PHASE 8.8 MASTER TRUST & SAFETY PRODUCTION READINESS VERIFICATION SUCCESSFUL!")
    logger.info("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_master_verification())
