"""
Unit tests for Reporting, Moderation, Dispute Resolution, and Administrative Actions.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.moderation.models import Dispute, PlatformReport
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
)
from app.moderation.service import (
    DisputeService,
    ModerationService,
    ReportService,
    ResolutionService,
)
from app.trust.schemas import RiskLevel


@pytest.mark.asyncio
async def test_create_report_workflow():
    """Verify filing a report creates report and moderation case wrapper."""
    reporter_id = "user_rep_100"
    req = ReportCreate(
        target_type=ReportTargetType.WORKER,
        target_id="worker_w999",
        category=ReportCategory.POOR_SERVICE,
        description="Worker did not complete assigned task.",
    )

    fake_report = PlatformReport.model_construct(
        report_id="rep_555",
        reporter_id=reporter_id,
        target_type=ReportTargetType.WORKER,
        target_id="worker_w999",
        category=ReportCategory.POOR_SERVICE,
        status=ReportStatus.SUBMITTED,
    )

    with patch("app.moderation.repository.ReportRepository.create_report", new_callable=AsyncMock, return_value=fake_report), \
         patch("app.moderation.repository.ModerationCaseRepository.create_case", new_callable=AsyncMock), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit:

        res = await ReportService.create_report(reporter_id, req)

        assert res.report_id == "rep_555"
        assert res.status == ReportStatus.SUBMITTED
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_moderation_review_report():
    """Verify moderator reviewing report and assigning severity."""
    mod_info = {"id": "admin_mod_1", "role": "admin", "email": "mod@kaamsetu.com"}
    req = ModerationReviewRequest(
        report_id="rep_555",
        severity=RiskLevel.HIGH,
        recommended_action=AdministrativeAction.TEMPORARY_RESTRICTION,
        notes="Multiple complaints received.",
    )

    fake_report = PlatformReport.model_construct(
        report_id="rep_555",
        reporter_id="user_rep_100",
        status=ReportStatus.SUBMITTED,
    )

    with patch("app.moderation.repository.ReportRepository.get_by_id", new_callable=AsyncMock, return_value=fake_report), \
         patch("app.moderation.repository.ReportRepository.update_report", new_callable=AsyncMock, return_value=fake_report), \
         patch("app.moderation.repository.ModerationCaseRepository.get_by_reference", new_callable=AsyncMock, return_value=None), \
         patch("app.moderation.repository.CaseNoteRepository.create_note", new_callable=AsyncMock), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        updated = await ModerationService.review_report(mod_info, req)
        assert updated.report_id == "rep_555"


@pytest.mark.asyncio
async def test_dispute_resolution_with_trust_score_penalty():
    """Verify resolving dispute with Trust Score penalty and administrative action."""
    mod_info = {"id": "admin_mod_1", "role": "admin", "email": "mod@kaamsetu.com"}
    req = DisputeResolveRequest(
        dispute_id="disp_888",
        resolution_decision="Respondent violated terms.",
        administrative_action=AdministrativeAction.TRUST_SCORE_ADJUSTMENT,
        target_user_id="target_user_555",
        trust_score_delta=-15.0,
    )

    fake_dispute = Dispute.model_construct(
        dispute_id="disp_888",
        initiator_id="initiator_111",
        respondent_id="target_user_555",
        status=DisputeStatus.SUBMITTED,
    )

    fake_user = MagicMock(role="worker", save=AsyncMock())
    fake_profile = MagicMock(trust_score=75.0)

    with patch("app.moderation.repository.DisputeRepository.get_by_id", new_callable=AsyncMock, return_value=fake_dispute), \
         patch("app.moderation.repository.DisputeRepository.update_dispute", new_callable=AsyncMock, return_value=fake_dispute), \
         patch("app.moderation.repository.CaseNoteRepository.create_note", new_callable=AsyncMock), \
         patch("app.auth.models.User.get", new_callable=AsyncMock, return_value=fake_user), \
         patch("app.trust.service.TrustService.get_or_create_profile", new_callable=AsyncMock, return_value=fake_profile), \
         patch("app.trust.service.TrustService.update_trust_score", new_callable=AsyncMock) as mock_update_score, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        res = await ResolutionService.resolve_dispute(mod_info, req)

        assert res.dispute_id == "disp_888"
        # Verify Trust Score updated (75.0 - 15.0 = 60.0)
        mock_update_score.assert_called_once()
        assert mock_update_score.call_args.kwargs["new_score"] == 60.0
