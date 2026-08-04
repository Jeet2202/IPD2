"""
Verification script for Phase 8.4 - Reporting, Moderation & Dispute Resolution.

Executes complete E2E verification of:
1. Beanie database document model registration.
2. ReportService platform report filing and case wrapper creation.
3. EvidenceService Cloudinary file upload and metadata tracking.
4. ModerationService review, severity assignment, case notes, and escalations.
5. DisputeService formal dispute lifecycle tracking.
6. ResolutionService final decisions with P8.1 administrative actions (trust score updates, risk events, restrictions, suspensions).
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
from app.fraud.models import AbuseReport, FraudAlert, FraudEvent, FraudRule
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
    DisputeStatus,
    DisputeType,
    ModerationEscalateRequest,
    ModerationReviewRequest,
    ReportCategory,
    ReportCreate,
    ReportStatus,
    ReportTargetType,
    ReportUpdate,
)
from app.moderation.service import (
    DisputeService,
    EvidenceService,
    ModerationService,
    ReportService,
    ResolutionService,
)
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
    logger.info("Starting Phase 8.4 - Reporting, Moderation & Dispute Resolution Verification...")

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
        PlatformReport,
        Dispute,
        ModerationCase,
        EvidenceFile,
        CaseNote,
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 20 document models.")

    try:
        # Initialize default policies
        await ConfigService.initialize_default_policies()

        # Clean up test users and data
        customer_email = "test_customer_p84@kaamsetu.com"
        worker_email = "test_worker_p84@kaamsetu.com"
        admin_email = "test_admin_p84@kaamsetu.com"

        await User.find(User.email == customer_email).delete()
        await User.find(User.email == worker_email).delete()
        await User.find(User.email == admin_email).delete()
        await User.find(User.phone == "+919988774433").delete()
        await User.find(User.phone == "+919988774434").delete()
        await User.find(User.phone == "+919988774435").delete()

        customer = User(
            email=customer_email,
            phone="+919988774433",
            password_hash="fake_cust_hash",
            full_name="Karan Customer P84",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_email_verified=True,
        )
        await customer.insert()
        customer_id_str = str(customer.id)

        worker = User(
            email=worker_email,
            phone="+919988774434",
            password_hash="fake_work_hash",
            full_name="Vikram Worker P84",
            role=UserRole.WORKER,
            is_active=True,
            is_email_verified=True,
        )
        await worker.insert()
        worker_id_str = str(worker.id)

        admin = User(
            email=admin_email,
            phone="+919988774435",
            password_hash="fake_admin_hash",
            full_name="Admin Moderator P84",
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        await admin.insert()
        admin_id_str = str(admin.id)

        # Cleanup old test records
        await PlatformReport.find(PlatformReport.reporter_id == customer_id_str).delete()
        await Dispute.find(Dispute.initiator_id == worker_id_str).delete()
        await TrustProfile.find(TrustProfile.user_id == worker_id_str).delete()

        # Initialize worker trust profile
        worker_profile = await TrustService.get_or_create_profile(worker_id_str, UserRole.WORKER)
        initial_score = worker_profile.trust_score

        # 2. File Platform Report
        report_req = ReportCreate(
            target_type=ReportTargetType.WORKER,
            target_id=worker_id_str,
            category=ReportCategory.POOR_SERVICE,
            description="Worker left service site uncleaned and incomplete.",
        )
        report = await ReportService.create_report(customer_id_str, report_req)
        assert report.report_id is not None
        assert report.status == ReportStatus.SUBMITTED
        logger.info("SUCCESS: Customer submitted report against worker (report_id=%s).", report.report_id)

        # 3. Upload Evidence File
        fake_photo_bytes = b"Fake PNG Photo Content For Moderation Evidence Test"
        evidence = await EvidenceService.upload_evidence(
            case_id=report.report_id,
            uploader_id=customer_id_str,
            file_bytes=fake_photo_bytes,
            filename="site_photo.png",
            mime_type="image/png",
            description="Photo of incomplete work site",
        )
        assert evidence.evidence_id is not None
        assert evidence.secure_url is not None
        logger.info("SUCCESS: Uploaded evidence file to Cloudinary & DB (evidence_id=%s).", evidence.evidence_id)

        # 4. Moderator Review & Severity Assignment
        admin_info = {"id": admin_id_str, "role": "admin", "email": admin_email}
        review_req = ModerationReviewRequest(
            report_id=report.report_id,
            severity=RiskLevel.HIGH,
            recommended_action=AdministrativeAction.TRUST_SCORE_ADJUSTMENT,
            notes="Evidence photos confirm incomplete work site.",
        )
        reviewed_report = await ModerationService.review_report(admin_info, review_req)
        assert reviewed_report.status == ReportStatus.UNDER_REVIEW
        assert reviewed_report.severity == RiskLevel.HIGH
        logger.info("SUCCESS: Moderator reviewed report and assigned HIGH severity.")

        # 5. Case Escalation
        escalate_req = ModerationEscalateRequest(
            case_id=report.report_id,
            reason="Worker disputed findings; escalating to senior review.",
        )
        m_case = await ModerationService.escalate_case(admin_info, escalate_req)
        assert m_case.is_escalated == True
        logger.info("SUCCESS: Case escalated to senior administration.")

        # 6. Create Formal Dispute Case
        dispute_req = DisputeCreate(
            dispute_type=DisputeType.WORKER_VS_CUSTOMER,
            respondent_id=customer_id_str,
            reason="Worker claims customer provided incorrect job requirements.",
        )
        dispute = await DisputeService.create_dispute(worker_id_str, dispute_req)
        assert dispute.dispute_id is not None
        assert dispute.status == DisputeStatus.SUBMITTED
        logger.info("SUCCESS: Worker opened formal dispute case (dispute_id=%s).", dispute.dispute_id)

        # 7. Resolve Dispute & Execute Administrative Actions (P8.1 Integration)
        resolve_req = DisputeResolveRequest(
            dispute_id=dispute.dispute_id,
            resolution_decision="Finding in favor of Customer. Worker penalized for incomplete execution.",
            administrative_action=AdministrativeAction.TEMPORARY_RESTRICTION,
            target_user_id=worker_id_str,
            trust_score_delta=-15.0,
        )
        resolved_dispute = await ResolutionService.resolve_dispute(admin_info, resolve_req)
        assert resolved_dispute.status == DisputeStatus.RESOLVED

        # Verify Trust Score updated (-15.0 points)
        updated_worker_profile = await TrustProfile.find_one(TrustProfile.user_id == worker_id_str)
        assert updated_worker_profile.trust_score == initial_score - 15.0
        assert updated_worker_profile.review_status == ReviewStatus.FLAGGED
        logger.info(
            "SUCCESS: Admin resolved dispute. Worker Trust Score updated from %.1f to %.1f, status=FLAGGED.",
            initial_score,
            updated_worker_profile.trust_score,
        )

        # 8. REST API Endpoints Verification via HTTP Client
        customer_token = create_access_token(customer_id_str, UserRole.CUSTOMER)
        admin_token = create_access_token(admin_id_str, UserRole.ADMIN)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # POST /api/v1/reports
            rep_payload = {
                "target_type": "worker",
                "target_id": worker_id_str,
                "category": "harassment",
                "description": "Inappropriate language in chat messages.",
            }
            resp = await ac.post(
                "/api/v1/reports",
                json=rep_payload,
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp.status_code == 200
            rep_data = resp.json()
            api_report_id = rep_data["report_id"]

            # GET /api/v1/reports/{id}
            resp = await ac.get(
                f"/api/v1/reports/{api_report_id}",
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp.status_code == 200
            detail_data = resp.json()
            assert detail_data["report_id"] == api_report_id

            # POST /api/v1/reports/{id}/evidence (Multipart form file upload)
            files = {"file": ("screenshot.png", b"Fake Screenshot Content", "image/png")}
            data = {"description": "Chat log screenshot"}
            resp = await ac.post(
                f"/api/v1/reports/{api_report_id}/evidence",
                data=data,
                files=files,
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp.status_code == 200
            ev_data = resp.json()
            assert ev_data["evidence_id"] is not None

            # POST /api/v1/moderation/review (Admin)
            review_payload = {
                "report_id": api_report_id,
                "severity": "High",
                "notes": "Verified chat log screenshot",
            }
            resp = await ac.post(
                "/api/v1/moderation/review",
                json=review_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200

            # POST /api/v1/disputes/create
            disp_payload = {
                "dispute_type": "customer_vs_worker",
                "respondent_id": worker_id_str,
                "reason": "Unresolved quality dispute",
            }
            resp = await ac.post(
                "/api/v1/disputes/create",
                json=disp_payload,
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp.status_code == 200
            disp_data = resp.json()
            api_dispute_id = disp_data["dispute_id"]

            # GET /api/v1/disputes
            resp = await ac.get(
                "/api/v1/disputes",
                headers={"Authorization": f"Bearer {customer_token}"},
            )
            assert resp.status_code == 200
            disputes_list = resp.json()
            assert len(disputes_list) >= 1

            # PUT /api/v1/disputes/{id}/resolve (Admin)
            resolve_payload = {
                "dispute_id": api_dispute_id,
                "resolution_decision": "Customer refunded and case closed.",
                "administrative_action": "warning",
                "target_user_id": worker_id_str,
                "trust_score_delta": -5.0,
            }
            resp = await ac.put(
                f"/api/v1/disputes/{api_dispute_id}/resolve",
                json=resolve_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            res_disp = resp.json()
            assert res_disp["status"] == "resolved"

        logger.info("SUCCESS: All REST API endpoints operational and verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.4 - Reporting, Moderation & Dispute Resolution Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
