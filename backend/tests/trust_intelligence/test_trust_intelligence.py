"""
Unit tests for Trust Intelligence & Risk Assessment services.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
import pytest

from app.trust_intelligence.schemas import (
    ComplianceIntelligenceRead,
    FraudIntelligenceRead,
    ModerationIntelligenceRead,
    RiskLevelGrade,
    SecurityIntelligenceRead,
    TrustOverviewRead,
)
from app.trust_intelligence.service import (
    RiskAssessmentService,
    RiskTrendService,
    TrustRecommendationService,
    TrustSummaryService,
)


@pytest.mark.asyncio
async def test_trust_overview_calculation():
    """Verify platform trust overview aggregation."""
    with patch("app.trust.models.TrustProfile.find_all") as mock_tp_find, \
         patch("app.verification.models.WorkerVerification.find_all") as mock_wv_find:

        mock_tp_find.return_value.to_list = AsyncMock(return_value=[])
        mock_wv_find.return_value.to_list = AsyncMock(return_value=[])

        overview = await TrustSummaryService.get_trust_overview()
        assert overview.average_trust_score == 100.0
        assert overview.total_workers == 0


@pytest.mark.asyncio
async def test_risk_assessment_calculation():
    """Verify weighted department risk score and overall risk grade calculation."""
    now = datetime.now(timezone.utc)
    fake_overview = TrustOverviewRead(
        average_trust_score=85.0,
        trust_distribution={"90-100": 10},
        total_workers=10,
        verified_workers_count=8,
        pending_verifications_count=2,
        restricted_accounts_count=0,
        high_risk_users_count=0,
        generated_at=now,
    )
    fake_fraud = FraudIntelligenceRead(
        active_fraud_cases_count=1,
        high_risk_accounts_count=0,
        rule_trigger_stats={},
        fraud_resolution_rate_percentage=100.0,
        generated_at=now,
    )
    fake_mod = ModerationIntelligenceRead(
        pending_reports_count=2,
        escalated_reports_count=0,
        open_disputes_count=1,
        avg_resolution_time_hours=4.0,
        generated_at=now,
    )
    fake_comp = ComplianceIntelligenceRead(
        privacy_requests_count=0,
        data_export_requests_count=0,
        pending_compliance_tasks_count=0,
        consent_granted_percentages={},
        generated_at=now,
    )
    fake_sec = SecurityIntelligenceRead(
        failed_logins_24h=1,
        api_auth_failures_24h=0,
        active_security_alerts_count=0,
        critical_security_events_24h=0,
        generated_at=now,
    )

    with patch("app.trust_intelligence.service.TrustSummaryService.get_trust_overview", new_callable=AsyncMock, return_value=fake_overview), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_fraud_intelligence", new_callable=AsyncMock, return_value=fake_fraud), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_moderation_intelligence", new_callable=AsyncMock, return_value=fake_mod), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_compliance_intelligence", new_callable=AsyncMock, return_value=fake_comp), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_security_intelligence", new_callable=AsyncMock, return_value=fake_sec), \
         patch("app.trust_intelligence.repository.TrustIntelligenceRepository.create_snapshot", new_callable=AsyncMock):

        assessment = await RiskAssessmentService.get_risk_assessment()
        assert assessment.overall_risk_score >= 0.0
        assert len(assessment.department_scores) == 5
        assert assessment.platform_health in ["healthy", "warning", "critical"]


@pytest.mark.asyncio
async def test_recommendations_generation_with_metric_citations():
    """Verify metric-referenced recommendation generation."""
    now = datetime.now(timezone.utc)
    fake_overview = TrustOverviewRead(
        average_trust_score=85.0,
        trust_distribution={},
        total_workers=10,
        verified_workers_count=6,
        pending_verifications_count=4,
        restricted_accounts_count=0,
        high_risk_users_count=0,
        generated_at=now,
    )
    fake_sec = SecurityIntelligenceRead(
        failed_logins_24h=6,
        api_auth_failures_24h=0,
        active_security_alerts_count=1,
        critical_security_events_24h=0,
        generated_at=now,
    )
    fake_mod = ModerationIntelligenceRead(
        pending_reports_count=1,
        escalated_reports_count=0,
        open_disputes_count=2,
        avg_resolution_time_hours=4.0,
        generated_at=now,
    )
    fake_fraud = FraudIntelligenceRead(
        active_fraud_cases_count=0,
        high_risk_accounts_count=0,
        rule_trigger_stats={},
        fraud_resolution_rate_percentage=100.0,
        generated_at=now,
    )
    fake_comp = ComplianceIntelligenceRead(
        privacy_requests_count=0,
        data_export_requests_count=0,
        pending_compliance_tasks_count=0,
        consent_granted_percentages={},
        generated_at=now,
    )

    with patch("app.trust_intelligence.service.TrustSummaryService.get_trust_overview", new_callable=AsyncMock, return_value=fake_overview), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_security_intelligence", new_callable=AsyncMock, return_value=fake_sec), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_moderation_intelligence", new_callable=AsyncMock, return_value=fake_mod), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_fraud_intelligence", new_callable=AsyncMock, return_value=fake_fraud), \
         patch("app.trust_intelligence.service.TrustSummaryService.get_compliance_intelligence", new_callable=AsyncMock, return_value=fake_comp):

        recs = await TrustRecommendationService.get_recommendations()
        assert len(recs) >= 3
        # Check that metric citations are included
        verif_rec = next(r for r in recs if r.department.value == "verification")
        assert "Pending Verifications Backlog = 4" in verif_rec.metric_citation
