"""
Domain services for Fraud Detection & Abuse Prevention.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.core.exceptions import NotFoundException
from app.fraud.engine import FraudRuleEngine
from app.fraud.models import (
    AbuseReport,
    FraudAlert,
    FraudEvent,
    FraudRule,
)
from app.fraud.repository import (
    AbuseReportRepository,
    FraudAlertRepository,
    FraudEventRepository,
    FraudRuleRepository,
)
from app.fraud.schemas import (
    AbuseReportCreate,
    AbuseType,
    AlertPriority,
    AlertStatus,
    AutomatedAction,
    FraudAnalysisRequest,
    FraudAnalysisResponse,
    FraudRuleCreate,
    FraudRuleType,
    FraudRuleUpdate,
    FraudStatisticsRead,
    TriggeredRuleDetail,
)
from app.trust.models import ReviewStatus
from app.trust.repository import TrustProfileRepository
from app.trust.schemas import AuditEventType, RiskEventType, RiskLevel
from app.trust.service import AuditService, RiskService, TrustService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Default Fraud Rules Initializer Definitions
# ---------------------------------------------------------------------------

DEFAULT_FRAUD_RULES = [
    {
        "rule_key": "multiple_failed_logins",
        "name": "Multiple Failed Login Attempts",
        "description": "Detects excessive authentication failures within a short time window.",
        "rule_type": FraudRuleType.MULTIPLE_FAILED_LOGINS,
        "severity": RiskLevel.HIGH,
        "score_impact": 25.0,
        "thresholds": {"max_attempts": 5},
    },
    {
        "rule_key": "duplicate_account_attempt",
        "name": "Duplicate Account / Identity Matching",
        "description": "Detects multiple accounts attempting to use identical phone, email, or device fingerprints.",
        "rule_type": FraudRuleType.DUPLICATE_ACCOUNT_ATTEMPT,
        "severity": RiskLevel.HIGH,
        "score_impact": 30.0,
        "thresholds": {"max_matches": 1},
    },
    {
        "rule_key": "rapid_booking_creation",
        "name": "Rapid Booking Velocity",
        "description": "Detects automated bot-like booking creation velocity.",
        "rule_type": FraudRuleType.RAPID_BOOKING_CREATION,
        "severity": RiskLevel.MEDIUM,
        "score_impact": 20.0,
        "thresholds": {"max_bookings_per_hour": 5},
    },
    {
        "rule_key": "excessive_cancellation",
        "name": "Excessive Booking Cancellation",
        "description": "Detects accounts cancelling an unusually high percentage of bookings.",
        "rule_type": FraudRuleType.EXCESSIVE_CANCELLATION,
        "severity": RiskLevel.MEDIUM,
        "score_impact": 20.0,
        "thresholds": {"max_cancellation_rate": 0.5, "max_cancellations_24h": 4},
    },
    {
        "rule_key": "suspicious_quotation_activity",
        "name": "Suspicious Quotation Patterns",
        "description": "Detects abnormal pricing spikes or rapid worker quotation bursts.",
        "rule_type": FraudRuleType.SUSPICIOUS_QUOTATION_ACTIVITY,
        "severity": RiskLevel.HIGH,
        "score_impact": 25.0,
        "thresholds": {"max_deviation_multiplier": 3.0, "max_quotes_10m": 10},
    },
    {
        "rule_key": "repeated_verification_failures",
        "name": "Repeated Document Verification Failures",
        "description": "Detects repeated identity or document upload rejections.",
        "rule_type": FraudRuleType.REPEATED_VERIFICATION_FAILURES,
        "severity": RiskLevel.HIGH,
        "score_impact": 25.0,
        "thresholds": {"max_failures": 3},
    },
    {
        "rule_key": "spam_behaviour",
        "name": "Spam & Repeated Content",
        "description": "Detects automated spam messaging or identical bulk submissions.",
        "rule_type": FraudRuleType.SPAM_BEHAVIOUR,
        "severity": RiskLevel.MEDIUM,
        "score_impact": 15.0,
        "thresholds": {"max_identical_messages": 5},
    },
    {
        "rule_key": "review_abuse",
        "name": "Review Manipulation & Rating Stuffing",
        "description": "Detects suspicious rating patterns or rapid review postings.",
        "rule_type": FraudRuleType.REVIEW_ABUSE,
        "severity": RiskLevel.HIGH,
        "score_impact": 30.0,
        "thresholds": {"max_reviews_per_hour": 5},
    },
    {
        "rule_key": "excessive_profile_updates",
        "name": "Excessive Profile Modifications",
        "description": "Detects rapid profile churn intended to evade filters.",
        "rule_type": FraudRuleType.EXCESSIVE_PROFILE_UPDATES,
        "severity": RiskLevel.LOW,
        "score_impact": 15.0,
        "thresholds": {"max_updates_per_hour": 6},
    },
    {
        "rule_key": "unusual_login_location",
        "name": "Unusual Geolocation / Unverified IP",
        "description": "Detects authentication anomalies from unverified countries or proxies.",
        "rule_type": FraudRuleType.UNUSUAL_LOGIN_LOCATION,
        "severity": RiskLevel.MEDIUM,
        "score_impact": 20.0,
        "thresholds": {},
    },
    {
        "rule_key": "suspicious_api_patterns",
        "name": "Anomalous API Traffic Bursts",
        "description": "Detects bot scraper or rate limit violation spikes.",
        "rule_type": FraudRuleType.SUSPICIOUS_API_PATTERNS,
        "severity": RiskLevel.CRITICAL,
        "score_impact": 35.0,
        "thresholds": {"max_rpm": 120},
    },
]


# ---------------------------------------------------------------------------
# Fraud Configuration Service
# ---------------------------------------------------------------------------

class FraudConfigService:
    """Manages fraud detection rule definitions and thresholds."""

    @staticmethod
    async def initialize_default_rules() -> None:
        """Ensure default rules exist in database."""
        for rule_def in DEFAULT_FRAUD_RULES:
            existing = await FraudRuleRepository.get_by_key(rule_def["rule_key"])
            if not existing:
                await FraudRuleRepository.create_rule(rule_def)
                logger.info("Initialized fraud rule in DB: %s", rule_def["rule_key"])

    @staticmethod
    async def list_active_rules() -> list[FraudRule]:
        """Fetch all active fraud rules."""
        return await FraudRuleRepository.list_active_rules()

    @staticmethod
    async def list_all_rules() -> list[FraudRule]:
        """Fetch all rules."""
        return await FraudRuleRepository.list_all_rules()

    @staticmethod
    async def get_rule(rule_key: str) -> FraudRule | None:
        """Fetch single rule by key."""
        return await FraudRuleRepository.get_by_key(rule_key)

    @staticmethod
    async def create_rule(rule_in: FraudRuleCreate, actor: dict[str, Any]) -> FraudRule:
        """Create a new fraud rule and log audit event."""
        rule = await FraudRuleRepository.create_rule(rule_in.model_dump())
        await AuditService.log_event(
            user_id="system",
            event_type=AuditEventType.POLICY_CHANGES,
            description=f"Created fraud rule '{rule.name}' ({rule.rule_key})",
            actor=actor,
            metadata={"rule_key": rule.rule_key},
        )
        return rule

    @staticmethod
    async def update_rule(
        rule_key: str,
        update_in: FraudRuleUpdate,
        actor: dict[str, Any],
    ) -> FraudRule | None:
        """Update an existing fraud rule."""
        updates = update_in.model_dump(exclude_unset=True)
        if not updates:
            return await FraudRuleRepository.get_by_key(rule_key)

        updated = await FraudRuleRepository.update_rule(rule_key, updates)
        if updated:
            await AuditService.log_event(
                user_id="system",
                event_type=AuditEventType.POLICY_CHANGES,
                description=f"Updated fraud rule '{updated.name}' ({rule_key})",
                actor=actor,
                metadata={"rule_key": rule_key, "updated_fields": list(updates.keys())},
            )
        return updated


# ---------------------------------------------------------------------------
# Risk Assessment Service
# ---------------------------------------------------------------------------

class RiskAssessmentService:
    """Computes risk scores, levels, reasons, and recommended actions."""

    @staticmethod
    def evaluate_risk(triggered_rules: list[TriggeredRuleDetail]) -> tuple[float, RiskLevel, str, AutomatedAction]:
        """
        Calculate total risk score, risk level, summary reason, and recommended action.
        """
        if not triggered_rules:
            return 0.0, RiskLevel.LOW, "No fraud rules triggered. Activity within normal parameters.", AutomatedAction.WARNING

        total_score = sum(r.score_impact for r in triggered_rules)
        total_score = min(100.0, total_score)

        if total_score >= 80.0:
            risk_level = RiskLevel.CRITICAL
            action = AutomatedAction.ACCOUNT_SUSPENSION
        elif total_score >= 60.0:
            risk_level = RiskLevel.HIGH
            action = AutomatedAction.TEMPORARY_RESTRICTION
        elif total_score >= 40.0:
            risk_level = RiskLevel.MEDIUM
            action = AutomatedAction.MANUAL_REVIEW
        else:
            risk_level = RiskLevel.LOW
            action = AutomatedAction.WARNING

        rule_names = [r.name for r in triggered_rules]
        reason = f"Fraud rules triggered: {', '.join(rule_names)}. Combined risk score: {total_score:.1f}/100."

        return total_score, risk_level, reason, action


# ---------------------------------------------------------------------------
# Alert Service
# ---------------------------------------------------------------------------

class AlertService:
    """Manages administrative fraud alerts."""

    @staticmethod
    async def generate_alert(
        user_id: str,
        title: str,
        description: str,
        risk_level: RiskLevel,
        triggered_rules: list[str],
    ) -> FraudAlert:
        """Generate and save an administrative fraud alert."""
        priority_map = {
            RiskLevel.CRITICAL: AlertPriority.CRITICAL,
            RiskLevel.HIGH: AlertPriority.HIGH,
            RiskLevel.MEDIUM: AlertPriority.MEDIUM,
            RiskLevel.LOW: AlertPriority.LOW,
        }

        alert = await FraudAlertRepository.create_alert({
            "user_id": str(user_id),
            "title": title,
            "description": description,
            "risk_level": risk_level,
            "priority": priority_map.get(risk_level, AlertPriority.MEDIUM),
            "status": AlertStatus.OPEN,
            "triggered_rules": triggered_rules,
        })
        logger.warning("Fraud Alert generated: alert_id=%s, user_id=%s, priority=%s", alert.alert_id, user_id, alert.priority.value)
        return alert

    @staticmethod
    async def list_alerts(
        user_id: str | None = None,
        status: AlertStatus | None = None,
        priority: AlertPriority | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[FraudAlert]:
        """List administrative fraud alerts."""
        return await FraudAlertRepository.list_alerts(
            user_id=user_id, status=status, priority=priority, skip=skip, limit=limit
        )

    @staticmethod
    async def resolve_alert(
        alert_id: str,
        action: str,
        resolution_notes: str,
        reviewer: dict[str, Any],
    ) -> FraudAlert | None:
        """Resolve or dismiss an alert."""
        alert = await FraudAlertRepository.resolve_alert(
            alert_id=alert_id,
            action=action,
            resolution_notes=resolution_notes,
            reviewer_id=reviewer.get("id"),
        )
        if alert:
            await AuditService.log_event(
                user_id=alert.user_id,
                event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
                description=f"Fraud alert [{alert_id}] marked as '{alert.status.value}'",
                actor=reviewer,
                metadata={"alert_id": alert_id, "notes": resolution_notes},
            )
        return alert


# ---------------------------------------------------------------------------
# Abuse Detection Service
# ---------------------------------------------------------------------------

class AbuseDetectionService:
    """Manages reports of spam, fake profiles, and review manipulation."""

    @staticmethod
    async def create_abuse_report(
        reporter_id: str,
        req: AbuseReportCreate,
    ) -> AbuseReport:
        """Submit an abuse report and trigger fraud analysis on target user."""
        report = await AbuseReportRepository.create_report({
            "reporter_id": str(reporter_id),
            "target_user_id": str(req.target_user_id),
            "abuse_type": req.abuse_type,
            "description": req.description,
            "evidence": req.evidence,
            "status": "pending",
        })

        await AuditService.log_event(
            user_id=req.target_user_id,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Abuse report filed [{req.abuse_type.value}]: {req.description[:50]}...",
            actor={"id": reporter_id, "role": "user"},
            metadata={"report_id": report.report_id, "abuse_type": req.abuse_type.value},
        )
        return report

    @staticmethod
    async def list_abuse_reports(skip: int = 0, limit: int = 50) -> list[AbuseReport]:
        """List all abuse reports."""
        return await AbuseReportRepository.list_all(skip=skip, limit=limit)

    @staticmethod
    async def resolve_abuse_report(
        report_id: str,
        action: str,
        resolution_notes: str,
        reviewer: dict[str, Any],
    ) -> AbuseReport | None:
        """Resolve or dismiss an abuse report."""
        report = await AbuseReportRepository.resolve_report(
            report_id=report_id,
            action=action,
            resolution_notes=resolution_notes,
        )
        if report:
            await AuditService.log_event(
                user_id=report.target_user_id,
                event_type=AuditEventType.ADMINISTRATIVE_ACTIONS,
                description=f"Abuse report [{report_id}] marked as '{report.status}'",
                actor=reviewer,
                metadata={"report_id": report_id, "notes": resolution_notes},
            )
        return report


# ---------------------------------------------------------------------------
# Fraud Detection Service
# ---------------------------------------------------------------------------

class FraudDetectionService:
    """Primary orchestrator for Fraud Detection & Abuse Prevention."""

    @staticmethod
    async def analyze_activity(req: FraudAnalysisRequest) -> FraudAnalysisResponse:
        """
        Analyze user event/activity payload against active rules, compute risk score,
        execute automated actions, generate alerts, and persist immutable event record.
        """
        user_id_str = str(req.user_id)

        # 1. Fetch active rules
        active_rules = await FraudConfigService.list_active_rules()

        # 2. Run Rule Engine evaluation
        triggered_rules = FraudRuleEngine.evaluate_rules(req.activity_data, active_rules)

        # 3. Compute Risk Assessment
        risk_score, risk_level, risk_reason, action = RiskAssessmentService.evaluate_risk(triggered_rules)

        triggered_keys = [r.rule_key for r in triggered_rules]

        # 4. Save FraudEvent record
        now = datetime.now(timezone.utc)
        event = await FraudEventRepository.create_event({
            "user_id": user_id_str,
            "event_type": req.event_type,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_reason": risk_reason,
            "triggered_rules": triggered_keys,
            "recommended_action": action.value,
            "event_data": req.activity_data,
            "created_at": now,
        })

        # 5. Automated Actions & Integration if Risk Level is Medium/High/Critical
        if risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            # Generate administrative Alert
            await AlertService.generate_alert(
                user_id=user_id_str,
                title=f"Fraud Alert: {risk_level.value} Risk Activity Detected",
                description=risk_reason,
                risk_level=risk_level,
                triggered_rules=triggered_keys,
            )

            # Record Risk Event in RiskService (P8.1)
            await RiskService.record_risk_event(
                user_id=user_id_str,
                event_type=RiskEventType.SUSPICIOUS_ACTIVITY,
                severity=risk_level,
                description=risk_reason,
                source="fraud_detection_engine",
                metadata={"event_id": event.event_id, "risk_score": risk_score},
            )

            # Update Trust Profile review_status (P8.1)
            target_review_status = (
                ReviewStatus.RESTRICTED if risk_level == RiskLevel.CRITICAL
                else ReviewStatus.FLAGGED if risk_level == RiskLevel.HIGH
                else ReviewStatus.UNDER_REVIEW
            )
            profile = await TrustProfileRepository.get_by_user_id(user_id_str)
            if profile and profile.review_status == ReviewStatus.CLEAR:
                await TrustProfileRepository.update_profile(user_id_str, {"review_status": target_review_status})

        # Audit Log (P8.1)
        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.RISK_EVENTS,
            description=f"Fraud Analysis [{req.event_type}]: Score {risk_score:.1f} ({risk_level.value})",
            actor={"id": "system", "role": "system"},
            metadata={"event_id": event.event_id, "triggered_count": len(triggered_rules)},
        )

        return FraudAnalysisResponse(
            user_id=user_id_str,
            risk_score=risk_score,
            risk_level=risk_level,
            risk_reason=risk_reason,
            triggered_rules=triggered_rules,
            recommended_action=action,
            event_id=event.event_id,
            analyzed_at=now,
        )

    @staticmethod
    async def get_fraud_events(
        user_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[FraudEvent]:
        """Fetch fraud analysis event history."""
        if user_id:
            return await FraudEventRepository.get_by_user(str(user_id), limit=limit)
        return await FraudEventRepository.list_all(skip=skip, limit=limit)

    @staticmethod
    async def get_statistics() -> FraudStatisticsRead:
        """Compute high-level platform fraud and risk metrics."""
        total = await FraudEventRepository.total_count()
        critical = await FraudEventRepository.count_by_risk_level(RiskLevel.CRITICAL)
        high = await FraudEventRepository.count_by_risk_level(RiskLevel.HIGH)
        medium = await FraudEventRepository.count_by_risk_level(RiskLevel.MEDIUM)

        open_alerts = await FraudAlertRepository.count_by_status(AlertStatus.OPEN)
        resolved_alerts = await FraudAlertRepository.count_by_status(AlertStatus.RESOLVED)
        pending_reports = await AbuseReportRepository.count_pending()

        return FraudStatisticsRead(
            total_events_analyzed=total,
            critical_risk_events=critical,
            high_risk_events=high,
            medium_risk_events=medium,
            open_alerts_count=open_alerts,
            resolved_alerts_count=resolved_alerts,
            pending_abuse_reports=pending_reports,
            generated_at=datetime.now(timezone.utc),
        )
