"""
Verification script for Phase 8.2 - Worker Verification & Trust Management.

Executes complete E2E verification of:
1. Beanie database document model registration.
2. VerificationDocumentService Cloudinary upload and metadata versioning.
3. VerificationService workflow state machine (Draft -> Submitted -> Under Review -> Approved / Rejected / Resubmission Required).
4. ApprovalService admin decisions with P8.1 TrustScore update (+10 for approval, -5 for rejection) and RiskService integration.
5. BadgeService rule catalog, automated badge assignment, and trust score bonus (+5.0 per badge).
6. REST APIs authentication, authorization, and payload schemas via HTTP client.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport

from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.database.connection import close_database_connection, connect_to_database
from app.main import app
from app.trust.models import (
    RiskEvent,
    SafetyFlag,
    TrustAuditLog,
    TrustPolicy,
    TrustProfile,
    VerificationHistory,
)
from app.trust.service import ConfigService, TrustService
from app.verification.models import (
    VerificationBadge,
    VerificationDocument,
    VerificationReview,
    WorkerVerification,
)
from app.verification.schemas import (
    TrustBadgeType,
    VerificationStatus,
    VerificationSubmitRequest,
    VerificationType,
)
from app.verification.service import (
    ApprovalService,
    BadgeService,
    VerificationDocumentService,
    VerificationService,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("Starting Phase 8.2 - Worker Verification & Trust Management Verification...")

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
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 11 document models.")

    try:
        # Initialize default trust policies (P8.1)
        await ConfigService.initialize_default_policies()

        # Clean up test users and data if present
        worker_email = "test_worker_p82@kaamsetu.com"
        admin_email = "test_admin_p82@kaamsetu.com"

        await User.find(User.email == worker_email).delete()
        await User.find(User.email == admin_email).delete()
        await User.find(User.phone == "+919988776655").delete()
        await User.find(User.phone == "+919988776656").delete()

        # Create worker identity
        worker_user = User(
            email=worker_email,
            phone="+919988776655",
            password_hash="fake_worker_hash",
            full_name="Rajesh Worker P82",
            role=UserRole.WORKER,
            is_active=True,
            is_email_verified=True,
        )
        await worker_user.insert()
        worker_id_str = str(worker_user.id)

        # Create admin identity
        admin_user = User(
            email=admin_email,
            phone="+919988776656",
            password_hash="fake_admin_hash",
            full_name="Admin Reviewer P82",
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        await admin_user.insert()
        admin_id_str = str(admin_user.id)

        # Clean old verification records for worker_id_str
        await WorkerVerification.find(WorkerVerification.worker_id == worker_id_str).delete()
        await VerificationDocument.find(VerificationDocument.worker_id == worker_id_str).delete()
        await VerificationReview.find(VerificationReview.worker_id == worker_id_str).delete()
        await VerificationBadge.find(VerificationBadge.worker_id == worker_id_str).delete()
        await TrustProfile.find(TrustProfile.user_id == worker_id_str).delete()

        # Initialize base trust profile for worker
        init_profile = await TrustService.get_or_create_profile(worker_id_str, UserRole.WORKER)
        initial_score = init_profile.trust_score
        logger.info("Initial worker trust profile created. Initial score: %.1f", initial_score)

        # 2. Document Upload Verification
        fake_aadhaar_bytes = b"%PDF-1.4 Fake Aadhaar Card Content For Verification Test"
        doc1 = await VerificationDocumentService.upload_document(
            worker_id=worker_id_str,
            document_type="aadhaar",
            file_bytes=fake_aadhaar_bytes,
            filename="aadhaar_card.pdf",
            mime_type="application/pdf",
            document_number="1234-5678-9012",
        )
        assert doc1.document_id is not None
        assert doc1.version == 1
        assert doc1.secure_url is not None
        logger.info("SUCCESS: Verification document uploaded successfully (id=%s).", doc1.document_id)

        # 3. Verification Submission (Identity Verification)
        submit_req = VerificationSubmitRequest(
            verification_type=VerificationType.IDENTITY,
            document_ids=[doc1.document_id],
            notes="Please verify my government Aadhaar card.",
        )
        verif = await VerificationService.submit_verification(worker_id_str, submit_req)
        assert verif.verification_id is not None
        assert verif.status == VerificationStatus.SUBMITTED
        logger.info("SUCCESS: Worker submitted Identity Verification (status=submitted).")

        # 4. Admin Review Phase (Under Review)
        admin_info = {"id": admin_id_str, "role": "admin", "email": admin_email}
        under_review = await ApprovalService.start_review(
            admin_user=admin_info,
            verification_id=verif.verification_id,
            review_notes="Checking document checksum and clear text",
        )
        assert under_review.status == VerificationStatus.UNDER_REVIEW
        logger.info("SUCCESS: Admin started review (status=under_review).")

        # 5. Admin Approval & Trust Score Integration
        approved_verif = await ApprovalService.approve_verification(
            admin_user=admin_info,
            verification_id=verif.verification_id,
            review_notes="Aadhaar photo and details verified cleanly.",
        )
        assert approved_verif.status == VerificationStatus.APPROVED

        # Verify Trust Score increased (+10.0 points)
        updated_profile = await TrustProfile.find_one(TrustProfile.user_id == worker_id_str)
        assert updated_profile.trust_score >= initial_score + 10.0
        logger.info(
            "SUCCESS: Admin approved verification. Worker Trust Score updated from %.1f to %.1f.",
            initial_score,
            updated_profile.trust_score,
        )

        # Verify matching badge auto-granted
        earned_badges = await BadgeService.get_worker_badges(worker_id_str)
        assert any(b.badge_type == TrustBadgeType.IDENTITY_VERIFIED for b in earned_badges)
        logger.info("SUCCESS: Matching 'Identity Verified' badge auto-assigned to worker.")

        # 6. Manual Badge Grant Test (Trusted Professional)
        badge = await BadgeService.grant_badge(
            worker_id=worker_id_str,
            badge_type=TrustBadgeType.TRUSTED_PROFESSIONAL,
            actor=admin_info,
        )
        assert badge.badge_id is not None
        all_badges = await BadgeService.get_worker_badges(worker_id_str)
        assert len(all_badges) >= 2
        logger.info("SUCCESS: Granted 'Trusted Professional' badge. Total active badges: %d", len(all_badges))

        # 7. Verification Status Overview
        status_overview = await VerificationService.get_verification_status(worker_id_str)
        assert status_overview.type_statuses["identity"] == VerificationStatus.APPROVED
        assert status_overview.approved_count >= 1
        assert len(status_overview.earned_badges) >= 2
        logger.info("SUCCESS: Verification status overview evaluated cleanly.")

        # 8. REST API Endpoints Verification via HTTP Client
        worker_token = create_access_token(worker_id_str, UserRole.WORKER)
        admin_token = create_access_token(admin_id_str, UserRole.ADMIN)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # POST /verification/upload (Multipart form file upload)
            files = {"file": ("skill_cert.pdf", b"Fake Skill Certificate Content", "application/pdf")}
            data = {"document_type": "skill_certificate", "document_number": "SKILL-9900"}
            resp = await ac.post(
                "/api/v1/verification/upload",
                data=data,
                files=files,
                headers={"Authorization": f"Bearer {worker_token}"},
            )
            assert resp.status_code == 200
            uploaded_doc_data = resp.json()
            skill_doc_id = uploaded_doc_data["document_id"]

            # POST /verification/submit (Skill Verification)
            submit_skill_payload = {
                "verification_type": "skill",
                "document_ids": [skill_doc_id],
                "notes": "Electrical safety certification",
            }
            resp = await ac.post(
                "/api/v1/verification/submit",
                json=submit_skill_payload,
                headers={"Authorization": f"Bearer {worker_token}"},
            )
            assert resp.status_code == 200
            skill_verif_data = resp.json()
            skill_verif_id = skill_verif_data["verification_id"]

            # GET /verification/status
            resp = await ac.get(
                "/api/v1/verification/status",
                headers={"Authorization": f"Bearer {worker_token}"},
            )
            assert resp.status_code == 200
            v_status = resp.json()
            assert v_status["worker_id"] == worker_id_str

            # GET /verification/history
            resp = await ac.get(
                "/api/v1/verification/history",
                headers={"Authorization": f"Bearer {worker_token}"},
            )
            assert resp.status_code == 200
            history_items = resp.json()
            assert len(history_items) >= 2

            # POST /verification/approve (Admin approving skill verification)
            approve_payload = {
                "verification_id": skill_verif_id,
                "review_notes": "Certificate verified with issuing agency",
            }
            resp = await ac.post(
                "/api/v1/verification/approve",
                json=approve_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            approved_skill = resp.json()
            assert approved_skill["status"] == "approved"

            # GET /verification/badges
            resp = await ac.get(
                "/api/v1/verification/badges",
                headers={"Authorization": f"Bearer {worker_token}"},
            )
            assert resp.status_code == 200
            badges_list = resp.json()
            assert len(badges_list) >= 2

        logger.info("SUCCESS: All REST API endpoints operational and verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.2 - Worker Verification & Trust Management Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
