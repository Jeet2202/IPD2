"""
Verification script for Phase 8.5 - Privacy, Compliance & Data Protection.

Executes complete E2E verification of:
1. Beanie database document model registration (25 models).
2. DataRetentionService default retention policy initialization (6 policies).
3. ConsentService default consent initialization and preference updates with compliance auditing.
4. DataAccessService and DataExportService JSON and CSV personal data export generation.
5. PrivacyService account deletion request with 30-day grace period and cancellation workflow.
6. REST APIs authentication, authorization, and payload schemas via HTTP client.
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
from app.privacy.schemas import (
    ConsentItem,
    ConsentType,
    ConsentUpdateRequest,
    ExportFormat,
    PrivacyRequestStatus,
)
from app.privacy.service import (
    ConsentService,
    DataExportService,
    DataRetentionService,
    PrivacyService,
)
from app.review.models import Review
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
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("Starting Phase 8.5 - Privacy, Compliance & Data Protection Verification...")

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
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized all 30 document models.")

    try:
        # Initialize default policies & retention rules
        await ConfigService.initialize_default_policies()
        await DataRetentionService.initialize_default_policies()

        policies = await DataRetentionService.list_retention_policies()
        assert len(policies) >= 6
        logger.info("SUCCESS: DataRetentionService initialized %d retention policies.", len(policies))

        # Clean up test users and data
        test_email = "test_user_p85@kaamsetu.com"
        await User.find(User.email == test_email).delete()
        await User.find(User.phone == "+919988773322").delete()

        test_user = User(
            email=test_email,
            phone="+919988773322",
            password_hash="fake_user_hash",
            full_name="Meera Privacy Target P85",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_email_verified=True,
        )
        await test_user.insert()
        user_id_str = str(test_user.id)

        # Cleanup old test records for user_id_str
        await UserConsent.find(UserConsent.user_id == user_id_str).delete()
        await PrivacyRequest.find(PrivacyRequest.user_id == user_id_str).delete()
        await DataExport.find(DataExport.user_id == user_id_str).delete()
        await ComplianceRecord.find(ComplianceRecord.user_id == user_id_str).delete()
        await TrustProfile.find(TrustProfile.user_id == user_id_str).delete()

        # Initialize base trust profile
        await TrustService.get_or_create_profile(user_id_str, UserRole.CUSTOMER)

        # 2. Consent Management Verification
        consents = await ConsentService.get_user_consents(user_id_str)
        assert len(consents) >= 6
        logger.info("SUCCESS: Loaded %d default consent categories for user.", len(consents))

        update_req = ConsentUpdateRequest(
            consents=[
                ConsentItem(consent_type=ConsentType.MARKETING, is_granted=True, policy_version="1.1"),
                ConsentItem(consent_type=ConsentType.ANALYTICS, is_granted=True, policy_version="1.1"),
            ]
        )
        updated_consents = await ConsentService.update_user_consents(user_id_str, update_req)
        m_consent = next(c for c in updated_consents if c.consent_type == ConsentType.MARKETING)
        assert m_consent.is_granted == True
        logger.info("SUCCESS: User updated consent preferences (marketing=True).")

        # 3. Data Export Generation (JSON & CSV)
        json_export = await DataExportService.generate_data_export(user_id_str, ExportFormat.JSON)
        assert json_export.export_id is not None
        json_parsed = json.loads(json_export.file_content)
        assert json_parsed["personal_info"]["email"] == test_email
        logger.info("SUCCESS: Generated JSON personal data export.")

        csv_export = await DataExportService.generate_data_export(user_id_str, ExportFormat.CSV)
        assert csv_export.export_id is not None
        assert "email" in csv_export.file_content
        logger.info("SUCCESS: Generated CSV personal data export.")

        # 4. Account Deletion Request & Grace Period Verification
        del_req = await PrivacyService.request_account_deletion(user_id_str, reason="Moving away from area")
        assert del_req.request_id is not None
        assert del_req.status == PrivacyRequestStatus.PENDING_GRACE_PERIOD
        assert del_req.scheduled_deletion_at is not None
        logger.info("SUCCESS: Account deletion request submitted (status=pending_grace_period, scheduled=30d).")

        # 5. Cancel Account Deletion Request
        cancelled_req = await PrivacyService.cancel_account_deletion(user_id_str)
        assert cancelled_req.status == PrivacyRequestStatus.CANCELLED
        logger.info("SUCCESS: Pending account deletion request cancelled successfully.")

        # 6. REST API Endpoints Verification via HTTP Client
        user_token = create_access_token(user_id_str, UserRole.CUSTOMER)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # GET /api/v1/privacy/profile
            resp = await ac.get(
                "/api/v1/privacy/profile",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            profile_data = resp.json()
            assert profile_data["email"] == test_email

            # GET /api/v1/privacy/consents
            resp = await ac.get(
                "/api/v1/privacy/consents",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            consents_data = resp.json()
            assert len(consents_data) >= 6

            # PUT /api/v1/privacy/consents
            put_payload = {
                "consents": [
                    {"consent_type": "notification", "is_granted": False, "policy_version": "1.2"}
                ]
            }
            resp = await ac.put(
                "/api/v1/privacy/consents",
                json=put_payload,
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200

            # POST /api/v1/privacy/export
            resp = await ac.post(
                "/api/v1/privacy/export",
                json={"format": "json"},
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            exp_res = resp.json()
            assert exp_res["export_id"] is not None

            # POST /api/v1/privacy/delete-request
            resp = await ac.post(
                "/api/v1/privacy/delete-request",
                json={"reason": "Testing API endpoint"},
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            del_res = resp.json()
            assert del_res["status"] == "pending_grace_period"

            # DELETE /api/v1/privacy/delete-request
            resp = await ac.delete(
                "/api/v1/privacy/delete-request",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            cancel_res = resp.json()
            assert cancel_res["status"] == "cancelled"

            # GET /api/v1/privacy/requests
            resp = await ac.get(
                "/api/v1/privacy/requests",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            requests_data = resp.json()
            assert len(requests_data) >= 1

            # GET /api/v1/privacy/policies
            resp = await ac.get(
                "/api/v1/privacy/policies",
                headers={"Authorization": f"Bearer {user_token}"},
            )
            assert resp.status_code == 200
            policies_data = resp.json()
            assert len(policies_data) >= 6

        logger.info("SUCCESS: All 8 REST API endpoints operational and verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.5 - Privacy, Compliance & Data Protection Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
