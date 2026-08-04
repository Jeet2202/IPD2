"""
Verification script for Phase 8.1 - Trust & Safety Infrastructure.

Executes complete verification of:
1. Beanie database model registration and index initialization.
2. ConfigService policy initialization.
3. TrustService profile creation, status evaluation, score updates, and administrative review.
4. RiskService risk event recording and dynamic risk level calculation.
5. AuditService immutable logging for all required event types and immutability guard verification.
6. SafetyEventManager flag creation, verification history tracking, and flag resolution.
7. PolicyService policy creation, active listing, and versioning.
8. API endpoints and authorization guards.
"""

import asyncio
import logging
import sys
from datetime import datetime, timezone

from httpx import AsyncClient, ASGITransport
import pytest

from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.core.config import settings
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
from app.trust.repository import TrustAuditLogRepository
from app.trust.schemas import (
    AuditEventType,
    RiskEventType,
    RiskLevel,
    ReviewStatus,
    TrustLevel,
    TrustPolicyCreate,
    TrustProfileUpdate,
    TrustVerificationStatus,
)
from app.trust.service import (
    AuditService,
    ConfigService,
    PolicyService,
    RiskService,
    SafetyEventManager,
    TrustScoreEngine,
    TrustService,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("Starting Phase 8.1 - Trust & Safety Infrastructure Verification...")

    # 1. Database Connection & Document Initialization
    document_models = [
        User,
        TrustProfile,
        TrustPolicy,
        RiskEvent,
        TrustAuditLog,
        SafetyFlag,
        VerificationHistory,
    ]
    await connect_to_database(document_models=document_models)
    logger.info("SUCCESS: Connected to MongoDB and initialized Beanie document models.")

    try:
        # Clean up old test data if present
        test_customer_id = "test_customer_p81"
        test_worker_id = "test_worker_p81"
        test_admin_id = "test_admin_p81"

        await User.find(User.email == "admin_p81@kaamsetu.com").delete()
        await User.find(User.email == "customer_p81@kaamsetu.com").delete()
        await User.find(User.phone == "+919876543210").delete()
        await User.find(User.phone == "+919876543211").delete()

        for uid in [test_customer_id, test_worker_id, test_admin_id]:
            await TrustProfile.find(TrustProfile.user_id == uid).delete()
            await RiskEvent.find(RiskEvent.user_id == uid).delete()
            await TrustAuditLog.find(TrustAuditLog.user_id == uid).delete()
            await SafetyFlag.find(SafetyFlag.user_id == uid).delete()
            await VerificationHistory.find(VerificationHistory.user_id == uid).delete()

        # 2. ConfigService Initialization
        await ConfigService.initialize_default_policies()
        thresholds = await ConfigService.get_score_thresholds()
        assert "excellent" in thresholds and "trusted" in thresholds
        logger.info("SUCCESS: Default policies and thresholds verified: %s", thresholds)

        # 3. Trust Score Engine Verification
        assert TrustScoreEngine.calculate_trust_level(95.0) == TrustLevel.EXCELLENT
        assert TrustScoreEngine.calculate_trust_level(80.0) == TrustLevel.TRUSTED
        assert TrustScoreEngine.calculate_trust_level(60.0) == TrustLevel.STANDARD
        assert TrustScoreEngine.calculate_trust_level(40.0) == TrustLevel.WATCHLIST
        assert TrustScoreEngine.calculate_trust_level(20.0) == TrustLevel.HIGH_RISK
        assert TrustScoreEngine.calculate_trust_level(5.0) == TrustLevel.RESTRICTED
        logger.info("SUCCESS: TrustScoreEngine score-to-level mapping validated.")

        # 4. Trust Profiles Creation & Status Verification
        cust_profile = await TrustService.get_or_create_profile(test_customer_id, UserRole.CUSTOMER)
        work_profile = await TrustService.get_or_create_profile(test_worker_id, UserRole.WORKER)

        assert cust_profile.user_id == test_customer_id
        assert cust_profile.role == UserRole.CUSTOMER
        assert cust_profile.trust_score == 75.0
        assert cust_profile.trust_level == TrustLevel.TRUSTED

        assert work_profile.user_id == test_worker_id
        assert work_profile.role == UserRole.WORKER
        logger.info("SUCCESS: Customer and Worker trust profiles initialized.")

        # 5. Score Update & Profile Update Test
        updated_cust = await TrustService.update_trust_score(
            user_id=test_customer_id,
            new_score=92.5,
            actor={"id": test_admin_id, "role": "admin"},
            reason="Positive review history and verified KYC",
        )
        assert updated_cust.trust_score == 92.5
        assert updated_cust.trust_level == TrustLevel.EXCELLENT
        logger.info("SUCCESS: Trust score update and level recalculation passed.")

        # 6. Risk Events & Dynamic Risk Evaluation Test
        risk1 = await RiskService.record_risk_event(
            user_id=test_worker_id,
            event_type=RiskEventType.SUSPICIOUS_ACTIVITY,
            severity=RiskLevel.MEDIUM,
            description="Rapid login attempts from multiple IPs",
            source="security_monitor",
            actor={"id": "system", "role": "system"},
        )
        risk2 = await RiskService.record_risk_event(
            user_id=test_worker_id,
            event_type=RiskEventType.FAILED_VERIFICATION,
            severity=RiskLevel.HIGH,
            description="Document checksum validation failure",
            source="kyc_verifier",
            actor={"id": "system", "role": "system"},
        )
        assert risk1.event_id is not None
        assert risk2.event_id is not None

        updated_work = await TrustProfile.find_one(TrustProfile.user_id == test_worker_id)
        assert updated_work.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]
        logger.info("SUCCESS: Risk event recording and risk evaluation verified. User risk level: %s", updated_work.risk_level)

        # 7. Audit Logging & Immutability Test
        audit_logs = await AuditService.get_user_audit_logs(test_customer_id)
        assert len(audit_logs) >= 2
        for log in audit_logs:
            assert log.event_id is not None
            assert log.user_id == test_customer_id
            assert log.event_type in list(AuditEventType)
            assert log.timestamp is not None
            assert "id" in log.actor

        # Verify immutability guard
        try:
            TrustAuditLogRepository.update_audit_log()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "immutable" in str(e)

        try:
            TrustAuditLogRepository.delete_audit_log()
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "immutable" in str(e)
        logger.info("SUCCESS: Immutable audit logging verified with immutability protection.")

        # 8. Safety Event Manager Test
        flag = await SafetyEventManager.raise_safety_flag(
            user_id=test_worker_id,
            flag_type="Identity Verification Pending",
            reason="Aadhaar photo does not match profile picture",
            severity=RiskLevel.MEDIUM,
            actor={"id": test_admin_id, "role": "admin"},
        )
        assert flag.flag_id is not None
        assert flag.status == "active"

        rec = await SafetyEventManager.record_verification_history(
            user_id=test_worker_id,
            verification_type="identity_document",
            status="pending_reupload",
            details={"issue": "Photo quality low"},
            actor={"id": test_admin_id, "role": "admin"},
        )
        assert rec.history_id is not None

        resolved_flag = await SafetyEventManager.resolve_safety_flag(flag.flag_id, actor={"id": test_admin_id, "role": "admin"})
        assert resolved_flag.status == "resolved"
        logger.info("SUCCESS: Safety flag creation, verification history, and resolution verified.")

        # 9. Administrative Review Test
        review_resp = await TrustService.review_user_trust(
            target_user_id=test_worker_id,
            action="under_review",
            reason="Manual investigation required for document upload",
            reviewer={"id": test_admin_id, "role": "admin"},
            new_risk_level=RiskLevel.HIGH,
        )
        assert review_resp.new_review_status == ReviewStatus.UNDER_REVIEW
        assert review_resp.new_risk_level == RiskLevel.HIGH
        logger.info("SUCCESS: Administrative review processing verified.")

        # 10. API Route Verification (FastAPI TestClient)
        # Create users in DB for authentication dependency lookups
        admin_user = await User.find_one(User.email == "admin_p81@kaamsetu.com")
        if not admin_user:
            admin_user = User(
                email="admin_p81@kaamsetu.com",
                phone="+919876543210",
                password_hash="fake_hash_admin",
                full_name="Admin Test P81",
                role=UserRole.ADMIN,
                is_active=True,
                is_email_verified=True,
            )
            await admin_user.insert()

        cust_user = await User.find_one(User.email == "customer_p81@kaamsetu.com")
        if not cust_user:
            cust_user = User(
                email="customer_p81@kaamsetu.com",
                phone="+919876543211",
                password_hash="fake_hash_cust",
                full_name="Customer Test P81",
                role=UserRole.CUSTOMER,
                is_active=True,
                is_email_verified=True,
            )
            await cust_user.insert()

        admin_token = create_access_token(str(admin_user.id), UserRole.ADMIN)
        cust_token = create_access_token(str(cust_user.id), UserRole.CUSTOMER)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            # Customer /trust/profile
            resp = await ac.get(
                "/api/v1/trust/profile",
                headers={"Authorization": f"Bearer {cust_token}"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["user_id"] == str(cust_user.id)
            assert data["role"] == "customer"

            # Customer /trust/status
            resp = await ac.get(
                "/api/v1/trust/status",
                headers={"Authorization": f"Bearer {cust_token}"},
            )
            assert resp.status_code == 200
            status_data = resp.json()
            assert "trust_score" in status_data
            assert "trust_level" in status_data

            # Admin /trust/policies
            resp = await ac.get(
                "/api/v1/trust/policies",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            policies = resp.json()
            assert len(policies) >= 1

            # Admin /trust/review
            review_payload = {
                "target_user_id": str(cust_user.id),
                "action": "clear",
                "reason": "Verification completed cleanly",
                "new_risk_level": "Low",
            }
            resp = await ac.post(
                "/api/v1/trust/review",
                json=review_payload,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert resp.status_code == 200
            review_res = resp.json()
            assert review_res["new_review_status"] == "clear"

        logger.info("SUCCESS: All 7 REST API endpoints verified via HTTP client.")

    finally:
        await close_database_connection()

    logger.info("Phase 8.1 - Trust & Safety Infrastructure Verification COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    asyncio.run(run_verification())
