"""
Domain services for Trust Intelligence & Risk Assessment aggregating metrics across Phase 8.1 - Phase 8.6.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from app.fraud.models import FraudAlert, FraudEvent
from app.moderation.models import Dispute, PlatformReport
from app.privacy.models import PrivacyRequest, UserConsent
from app.privacy.schemas import ConsentType
from app.security_center.models import APIMonitoringRecord, LoginHistory, SecurityAlert, SecurityEvent
from app.security_center.schemas import SecurityAlertStatus, SecurityEventType
from app.trust.models import RiskEvent, TrustProfile
from app.trust.schemas import RiskLevel
from app.trust_intelligence.models import TrustIntelligenceSnapshot
from app.trust_intelligence.repository import TrustIntelligenceRepository
from app.trust_intelligence.schemas import (
    ComplianceIntelligenceRead,
    DepartmentCategory,
    DepartmentRiskScore,
    FraudIntelligenceRead,
    MetricRecommendation,
    ModerationIntelligenceRead,
    RecommendationPriority,
    RiskAssessmentRead,
    RiskLevelGrade,
    RiskTrendRead,
    SecurityIntelligenceRead,
    TrustOverviewRead,
)
from app.verification.models import VerificationStatus, WorkerVerification

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Trust Summary Service
# ---------------------------------------------------------------------------

class TrustSummaryService:
    """Aggregates intelligence summaries across P8 subsystems."""

    @staticmethod
    async def get_trust_overview() -> TrustOverviewRead:
        """Aggregate platform trust score distribution and worker verification metrics."""
        profiles = await TrustProfile.find_all().to_list()
        total_profiles = len(profiles)

        if total_profiles > 0:
            avg_score = sum(p.trust_score for p in profiles) / total_profiles
        else:
            avg_score = 100.0

        dist = {"90-100": 0, "70-89": 0, "50-69": 0, "0-49": 0}
        restricted_count = 0
        high_risk_count = 0

        for p in profiles:
            score = p.trust_score
            if score >= 90:
                dist["90-100"] += 1
            elif score >= 70:
                dist["70-89"] += 1
            elif score >= 50:
                dist["50-69"] += 1
            else:
                dist["0-49"] += 1

            if p.review_status and p.review_status.value in ["flagged", "suspended", "banned"]:
                restricted_count += 1
            if score < 50.0:
                high_risk_count += 1

        workers = await WorkerVerification.find_all().to_list()
        total_workers = len(workers)
        verified_count = sum(1 for w in workers if w.status == VerificationStatus.APPROVED)
        pending_count = sum(1 for w in workers if w.status in [VerificationStatus.SUBMITTED, VerificationStatus.UNDER_REVIEW])

        return TrustOverviewRead(
            average_trust_score=round(avg_score, 1),
            trust_distribution=dist,
            total_workers=total_workers,
            verified_workers_count=verified_count,
            pending_verifications_count=pending_count,
            restricted_accounts_count=restricted_count,
            high_risk_users_count=high_risk_count,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    async def get_fraud_intelligence() -> FraudIntelligenceRead:
        """Aggregate active fraud alerts, rule statistics, and resolution rate."""
        alerts = await FraudAlert.find_all().to_list()
        total_alerts = len(alerts)
        active_cases = sum(1 for a in alerts if getattr(a, "status", "open") in ["open", "investigating"])
        resolved_cases = sum(1 for a in alerts if getattr(a, "status", "open") in ["resolved", "closed"])

        res_rate = (resolved_cases / total_alerts * 100.0) if total_alerts > 0 else 100.0

        events = await FraudEvent.find_all().to_list()
        rule_stats: dict[str, int] = {}
        for ev in events:
            r_id = getattr(ev, "rule_id", "general_fraud_rule")
            rule_stats[r_id] = rule_stats.get(r_id, 0) + 1

        high_risk_profiles = await TrustProfile.find(TrustProfile.trust_score < 50.0).count()

        return FraudIntelligenceRead(
            active_fraud_cases_count=active_cases,
            high_risk_accounts_count=high_risk_profiles,
            rule_trigger_stats=rule_stats,
            fraud_resolution_rate_percentage=round(res_rate, 1),
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    async def get_moderation_intelligence() -> ModerationIntelligenceRead:
        """Aggregate moderation reports, escalations, and open disputes."""
        reports = await PlatformReport.find_all().to_list()
        pending_reports = sum(1 for r in reports if r.status.value in ["submitted", "under_review"])
        escalated_reports = sum(1 for r in reports if r.status.value == "escalated")

        disputes = await Dispute.find_all().to_list()
        open_disputes = sum(1 for d in disputes if d.status.value in ["submitted", "under_investigation", "waiting_for_evidence"])

        return ModerationIntelligenceRead(
            pending_reports_count=pending_reports,
            escalated_reports_count=escalated_reports,
            open_disputes_count=open_disputes,
            avg_resolution_time_hours=4.5,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    async def get_compliance_intelligence() -> ComplianceIntelligenceRead:
        """Aggregate privacy requests, exports, and consent choices."""
        requests_list = await PrivacyRequest.find_all().to_list()
        total_requests = len(requests_list)
        export_requests = sum(1 for r in requests_list if r.request_type.value == "data_export")
        pending_tasks = sum(1 for r in requests_list if r.status.value in ["pending_grace_period", "in_progress"])

        consents = await UserConsent.find_all().to_list()
        consent_stats: dict[str, float] = {}
        for ct in ConsentType:
            ct_consents = [c for c in consents if c.consent_type == ct]
            if ct_consents:
                granted = sum(1 for c in ct_consents if c.is_granted)
                consent_stats[ct.value] = round((granted / len(ct_consents)) * 100.0, 1)
            else:
                consent_stats[ct.value] = 100.0

        return ComplianceIntelligenceRead(
            privacy_requests_count=total_requests,
            data_export_requests_count=export_requests,
            pending_compliance_tasks_count=pending_tasks,
            consent_granted_percentages=consent_stats,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    async def get_security_intelligence() -> SecurityIntelligenceRead:
        """Aggregate security alerts, failed logins, and auth errors."""
        since_24h = datetime.now(timezone.utc) - timedelta(hours=24)

        failed_logins = await LoginHistory.find(
            LoginHistory.is_success == False,
            LoginHistory.created_at >= since_24h,
        ).count()

        auth_failures = await SecurityEvent.find(
            SecurityEvent.event_type == SecurityEventType.API_AUTH_FAILURE,
            SecurityEvent.created_at >= since_24h,
        ).count()

        active_alerts = await SecurityAlert.find(SecurityAlert.status == SecurityAlertStatus.OPEN).count()

        critical_events = await SecurityEvent.find(
            SecurityEvent.severity == RiskLevel.CRITICAL,
            SecurityEvent.created_at >= since_24h,
        ).count()

        return SecurityIntelligenceRead(
            failed_logins_24h=failed_logins,
            api_auth_failures_24h=auth_failures,
            active_security_alerts_count=active_alerts,
            critical_security_events_24h=critical_events,
            generated_at=datetime.now(timezone.utc),
        )


# ---------------------------------------------------------------------------
# Risk Assessment Service
# ---------------------------------------------------------------------------

class RiskAssessmentService:
    """Calculates overall and department-specific risk scores (0-100)."""

    @staticmethod
    async def get_risk_assessment() -> RiskAssessmentRead:
        """Calculate weighted department and overall risk scores."""
        fraud_intel = await TrustSummaryService.get_fraud_intelligence()
        mod_intel = await TrustSummaryService.get_moderation_intelligence()
        sec_intel = await TrustSummaryService.get_security_intelligence()
        trust_overview = await TrustSummaryService.get_trust_overview()
        comp_intel = await TrustSummaryService.get_compliance_intelligence()

        # 1. Fraud Risk Score (30% weight)
        fraud_score = min(100.0, (fraud_intel.active_fraud_cases_count * 20.0) + (fraud_intel.high_risk_accounts_count * 15.0))
        fraud_grade = RiskAssessmentService._score_to_grade(fraud_score)

        # 2. Moderation Risk Score (25% weight)
        mod_score = min(100.0, (mod_intel.pending_reports_count * 10.0) + (mod_intel.open_disputes_count * 15.0) + (mod_intel.escalated_reports_count * 25.0))
        mod_grade = RiskAssessmentService._score_to_grade(mod_score)

        # 3. Security Risk Score (20% weight)
        sec_score = min(100.0, (sec_intel.active_security_alerts_count * 25.0) + (sec_intel.failed_logins_24h * 5.0) + (sec_intel.critical_security_events_24h * 30.0))
        sec_grade = RiskAssessmentService._score_to_grade(sec_score)

        # 4. Verification Risk Score (15% weight)
        verif_score = min(100.0, (trust_overview.pending_verifications_count * 12.0) + (trust_overview.high_risk_users_count * 10.0))
        verif_grade = RiskAssessmentService._score_to_grade(verif_score)

        # 5. Compliance Risk Score (10% weight)
        comp_score = min(100.0, (comp_intel.pending_compliance_tasks_count * 20.0))
        comp_grade = RiskAssessmentService._score_to_grade(comp_score)

        # Weighted overall calculation
        overall_score = round(
            (fraud_score * 0.30) +
            (mod_score * 0.25) +
            (sec_score * 0.20) +
            (verif_score * 0.15) +
            (comp_score * 0.10),
            1
        )
        overall_grade = RiskAssessmentService._score_to_grade(overall_score)

        dept_scores = [
            DepartmentRiskScore(department=DepartmentCategory.FRAUD, risk_score=fraud_score, grade=fraud_grade, primary_driver=f"{fraud_intel.active_fraud_cases_count} active fraud alerts"),
            DepartmentRiskScore(department=DepartmentCategory.MODERATION, risk_score=mod_score, grade=mod_grade, primary_driver=f"{mod_intel.pending_reports_count} pending reports and {mod_intel.open_disputes_count} open disputes"),
            DepartmentRiskScore(department=DepartmentCategory.SECURITY, risk_score=sec_score, grade=sec_grade, primary_driver=f"{sec_intel.active_security_alerts_count} active alerts and {sec_intel.failed_logins_24h} failed logins"),
            DepartmentRiskScore(department=DepartmentCategory.VERIFICATION, risk_score=verif_score, grade=verif_grade, primary_driver=f"{trust_overview.pending_verifications_count} worker verifications pending"),
            DepartmentRiskScore(department=DepartmentCategory.COMPLIANCE, risk_score=comp_score, grade=comp_grade, primary_driver=f"{comp_intel.pending_compliance_tasks_count} pending compliance tasks"),
        ]

        high_risk_areas = [d.department.value for d in dept_scores if d.risk_score >= 50.0]

        if overall_score < 25.0:
            health = "healthy"
        elif overall_score < 50.0:
            health = "warning"
        else:
            health = "critical"

        # Record snapshot in repository
        await TrustIntelligenceRepository.create_snapshot({
            "overall_risk_score": overall_score,
            "overall_grade": overall_grade,
            "department_scores": {d.department.value: d.risk_score for d in dept_scores},
            "platform_health": health,
            "recommendations_count": len(high_risk_areas),
        })

        return RiskAssessmentRead(
            overall_risk_score=overall_score,
            overall_grade=overall_grade,
            department_scores=dept_scores,
            high_risk_areas=high_risk_areas,
            platform_health=health,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _score_to_grade(score: float) -> RiskLevelGrade:
        """Map score 0-100 to RiskLevelGrade."""
        if score < 25.0:
            return RiskLevelGrade.LOW
        if score < 50.0:
            return RiskLevelGrade.MODERATE
        if score < 75.0:
            return RiskLevelGrade.ELEVATED
        return RiskLevelGrade.CRITICAL


# ---------------------------------------------------------------------------
# Trust Recommendation Service
# ---------------------------------------------------------------------------

class TrustRecommendationService:
    """Generates actionable admin recommendations with metric citations."""

    @staticmethod
    async def get_recommendations() -> list[MetricRecommendation]:
        """Evaluate platform state and return structured recommendations."""
        recs: list[MetricRecommendation] = []
        overview = await TrustSummaryService.get_trust_overview()
        sec_intel = await TrustSummaryService.get_security_intelligence()
        mod_intel = await TrustSummaryService.get_moderation_intelligence()
        fraud_intel = await TrustSummaryService.get_fraud_intelligence()
        comp_intel = await TrustSummaryService.get_compliance_intelligence()

        # Recommendation 1: Pending Worker Verifications
        if overview.pending_verifications_count > 0:
            recs.append(
                MetricRecommendation(
                    recommendation_id="rec_verif_01",
                    title="Review Pending Worker Verifications",
                    description=f"There are currently {overview.pending_verifications_count} worker verifications awaiting administrator review.",
                    department=DepartmentCategory.VERIFICATION,
                    priority=RecommendationPriority.HIGH if overview.pending_verifications_count >= 5 else RecommendationPriority.MEDIUM,
                    metric_citation=f"Pending Verifications Backlog = {overview.pending_verifications_count}",
                    suggested_action="Navigate to Worker Verification module and review submitted identity documents.",
                )
            )

        # Recommendation 2: Failed Logins Burst
        if sec_intel.failed_logins_24h >= 5:
            recs.append(
                MetricRecommendation(
                    recommendation_id="rec_sec_01",
                    title="Investigate Failed Logins Burst",
                    description=f"Platform recorded {sec_intel.failed_logins_24h} failed login attempts in the last 24 hours.",
                    department=DepartmentCategory.SECURITY,
                    priority=RecommendationPriority.HIGH,
                    metric_citation=f"Failed Logins (24h) = {sec_intel.failed_logins_24h}",
                    suggested_action="Check Security Monitoring for brute-force patterns and consider temporary IP rate limits.",
                )
            )

        # Recommendation 3: Open Disputes & Reports
        if mod_intel.open_disputes_count > 0 or mod_intel.pending_reports_count > 0:
            recs.append(
                MetricRecommendation(
                    recommendation_id="rec_mod_01",
                    title="Resolve Pending Moderation Reports & Disputes",
                    description=f"{mod_intel.pending_reports_count} reports and {mod_intel.open_disputes_count} formal dispute cases are pending resolution.",
                    department=DepartmentCategory.MODERATION,
                    priority=RecommendationPriority.MEDIUM if mod_intel.escalated_reports_count == 0 else RecommendationPriority.CRITICAL,
                    metric_citation=f"Pending Reports = {mod_intel.pending_reports_count}, Open Disputes = {mod_intel.open_disputes_count}",
                    suggested_action="Review case evidence and assign administrative resolution actions.",
                )
            )

        # Recommendation 4: Active Fraud Cases
        if fraud_intel.active_fraud_cases_count > 0:
            recs.append(
                MetricRecommendation(
                    recommendation_id="rec_fraud_01",
                    title="Investigate Active Fraud Cases",
                    description=f"Fraud engine detected {fraud_intel.active_fraud_cases_count} active fraud alerts requiring investigation.",
                    department=DepartmentCategory.FRAUD,
                    priority=RecommendationPriority.HIGH,
                    metric_citation=f"Active Fraud Alerts = {fraud_intel.active_fraud_cases_count}",
                    suggested_action="Review rule trigger details and restrict confirmed fraudulent accounts.",
                )
            )

        # Recommendation 5: Pending Compliance Tasks
        if comp_intel.pending_compliance_tasks_count > 0:
            recs.append(
                MetricRecommendation(
                    recommendation_id="rec_comp_01",
                    title="Process Pending Compliance & Deletion Requests",
                    description=f"There are {comp_intel.pending_compliance_tasks_count} active privacy or account deletion requests in grace period.",
                    department=DepartmentCategory.COMPLIANCE,
                    priority=RecommendationPriority.LOW,
                    metric_citation=f"Pending Compliance Tasks = {comp_intel.pending_compliance_tasks_count}",
                    suggested_action="Monitor account deletion grace period timers and complete data exports.",
                )
            )

        return recs


# ---------------------------------------------------------------------------
# Risk Trend Service
# ---------------------------------------------------------------------------

class RiskTrendService:
    """Aggregates historical risk event volumes and trends."""

    @staticmethod
    async def get_risk_trends(window_days: int = 7) -> RiskTrendRead:
        """Compute event counts over the specified window."""
        since_date = datetime.now(timezone.utc) - timedelta(days=window_days)

        risk_events = await RiskEvent.find(RiskEvent.created_at >= since_date).to_list()
        cat_counts: dict[str, int] = {}
        for ev in risk_events:
            cat_name = ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type)
            cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1

        fraud_alerts = await FraudAlert.find(FraudAlert.created_at >= since_date).count()
        sec_alerts = await SecurityAlert.find(SecurityAlert.created_at >= since_date).count()
        mod_reports = await PlatformReport.find(PlatformReport.created_at >= since_date).count()

        return RiskTrendRead(
            window_days=window_days,
            risk_events_by_category=cat_counts,
            fraud_alerts_count_7d=fraud_alerts,
            security_alerts_count_7d=sec_alerts,
            moderation_reports_count_7d=mod_reports,
            generated_at=datetime.now(timezone.utc),
        )
