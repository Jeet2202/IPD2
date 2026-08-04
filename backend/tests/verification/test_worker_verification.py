"""
Unit tests for Worker Verification & Trust Management services and workflow logic.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.trust.schemas import TrustLevel
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


@pytest.mark.asyncio
async def test_submit_verification():
    """Test worker submitting a verification request."""
    worker_id = "worker_v123"
    req = VerificationSubmitRequest(
        verification_type=VerificationType.IDENTITY,
        document_ids=["doc_111", "doc_222"],
        notes="Identity document attached",
    )

    fake_verification = MagicMock(
        verification_id="verif_999",
        worker_id=worker_id,
        verification_type=VerificationType.IDENTITY,
        status=VerificationStatus.SUBMITTED,
        document_ids=["doc_111", "doc_222"],
    )

    with patch("app.verification.repository.WorkerVerificationRepository.get_by_worker_and_type", new_callable=AsyncMock, return_value=None), \
         patch("app.verification.repository.WorkerVerificationRepository.create_verification", new_callable=AsyncMock, return_value=fake_verification), \
         patch("app.verification.repository.VerificationDocumentRepository.update_document", new_callable=AsyncMock), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit:

        res = await VerificationService.submit_verification(worker_id, req)

        assert res.verification_id == "verif_999"
        assert res.status == VerificationStatus.SUBMITTED
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_approve_verification_workflow():
    """Test admin approving verification request, updating trust score and granting badge."""
    admin_info = {"id": "admin_777", "role": "admin", "email": "admin@kaamsetu.com"}
    verification_id = "verif_identity_1"
    worker_id = "worker_v456"

    fake_verif = MagicMock(
        verification_id=verification_id,
        worker_id=worker_id,
        verification_type=VerificationType.IDENTITY,
        status=VerificationStatus.SUBMITTED,
        document_ids=["doc_1"],
    )

    fake_profile = MagicMock(
        user_id=worker_id,
        trust_score=75.0,
        trust_level=TrustLevel.TRUSTED,
    )

    with patch("app.verification.repository.WorkerVerificationRepository.get_by_id", new_callable=AsyncMock, return_value=fake_verif), \
         patch("app.verification.repository.WorkerVerificationRepository.update_verification", new_callable=AsyncMock, return_value=fake_verif), \
         patch("app.verification.repository.VerificationDocumentRepository.update_document", new_callable=AsyncMock), \
         patch("app.verification.repository.VerificationReviewRepository.create_review", new_callable=AsyncMock), \
         patch("app.trust.service.TrustService.get_or_create_profile", new_callable=AsyncMock, return_value=fake_profile), \
         patch("app.trust.service.TrustService.update_trust_score", new_callable=AsyncMock) as mock_update_score, \
         patch("app.verification.service.BadgeService.grant_badge", new_callable=AsyncMock) as mock_grant_badge, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        approved = await ApprovalService.approve_verification(admin_info, verification_id, review_notes="All clear")

        assert approved.verification_id == verification_id
        # Verify TrustScore update (+10 points to 85.0)
        mock_update_score.assert_called_once()
        call_kwargs = mock_update_score.call_args.kwargs
        assert call_kwargs["new_score"] == 85.0

        # Verify matching badge auto-granted
        mock_grant_badge.assert_called_once_with(
            worker_id=worker_id,
            badge_type=TrustBadgeType.IDENTITY_VERIFIED,
            actor=admin_info,
        )


@pytest.mark.asyncio
async def test_reject_verification_workflow():
    """Test admin rejecting verification request, triggering risk event and score deduction."""
    admin_info = {"id": "admin_777", "role": "admin", "email": "admin@kaamsetu.com"}
    verification_id = "verif_skill_2"
    worker_id = "worker_v789"

    fake_verif = MagicMock(
        verification_id=verification_id,
        worker_id=worker_id,
        verification_type=VerificationType.SKILL,
        status=VerificationStatus.SUBMITTED,
        document_ids=["doc_skill"],
    )

    fake_profile = MagicMock(
        user_id=worker_id,
        trust_score=75.0,
        trust_level=TrustLevel.TRUSTED,
    )

    with patch("app.verification.repository.WorkerVerificationRepository.get_by_id", new_callable=AsyncMock, return_value=fake_verif), \
         patch("app.verification.repository.WorkerVerificationRepository.update_verification", new_callable=AsyncMock, return_value=fake_verif), \
         patch("app.verification.repository.VerificationDocumentRepository.update_document", new_callable=AsyncMock), \
         patch("app.verification.repository.VerificationReviewRepository.create_review", new_callable=AsyncMock), \
         patch("app.trust.service.RiskService.record_risk_event", new_callable=AsyncMock) as mock_risk, \
         patch("app.trust.service.TrustService.get_or_create_profile", new_callable=AsyncMock, return_value=fake_profile), \
         patch("app.trust.service.TrustService.update_trust_score", new_callable=AsyncMock) as mock_update_score, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        rejected = await ApprovalService.reject_verification(
            admin_info, verification_id, review_notes="Invalid certificate", request_resubmission=False
        )

        assert rejected.verification_id == verification_id
        mock_risk.assert_called_once()
        mock_update_score.assert_called_once()
        assert mock_update_score.call_args.kwargs["new_score"] == 70.0


def test_badge_rules_catalog():
    """Verify available trust badge rules."""
    rules = BadgeService.list_badge_rules()
    badge_types = [r.badge_type for r in rules]
    assert TrustBadgeType.VERIFIED_WORKER in badge_types
    assert TrustBadgeType.IDENTITY_VERIFIED in badge_types
    assert TrustBadgeType.EXPERIENCED_WORKER in badge_types
    assert TrustBadgeType.TRUSTED_PROFESSIONAL in badge_types
