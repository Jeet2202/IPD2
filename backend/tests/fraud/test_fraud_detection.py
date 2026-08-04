"""
Unit tests for Fraud Detection Rule Engine, Risk Assessment, and Abuse Prevention.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.fraud.engine import FraudRuleEngine
from app.fraud.models import FraudEvent, FraudRule
from app.fraud.schemas import (
    AbuseReportCreate,
    AbuseType,
    AlertPriority,
    AlertStatus,
    AutomatedAction,
    FraudAnalysisRequest,
    FraudRuleType,
    TriggeredRuleDetail,
)
from app.fraud.service import (
    AbuseDetectionService,
    AlertService,
    FraudDetectionService,
    RiskAssessmentService,
)
from app.trust.schemas import RiskLevel


def test_rule_engine_failed_logins_trigger():
    """Verify rule engine triggers multiple_failed_logins rule when threshold exceeded."""
    rule = FraudRule.model_construct(
        rule_key="multiple_failed_logins",
        name="Multiple Failed Login Attempts",
        description="Detects excessive failed logins",
        rule_type=FraudRuleType.MULTIPLE_FAILED_LOGINS,
        severity=RiskLevel.HIGH,
        score_impact=25.0,
        thresholds={"max_attempts": 5},
        is_active=True,
    )

    # Activity below threshold
    triggered_below = FraudRuleEngine.evaluate_rules({"failed_logins": 3}, [rule])
    assert len(triggered_below) == 0

    # Activity exceeding threshold
    triggered_exceeded = FraudRuleEngine.evaluate_rules({"failed_logins": 6}, [rule])
    assert len(triggered_exceeded) == 1
    assert triggered_exceeded[0].rule_key == "multiple_failed_logins"
    assert triggered_exceeded[0].score_impact == 25.0


def test_rule_engine_multiple_rules():
    """Verify rule engine evaluating multiple active rules simultaneously."""
    rules = [
        FraudRule.model_construct(
            rule_key="rapid_booking_creation",
            name="Rapid Booking Velocity",
            description="Detects rapid bookings",
            rule_type=FraudRuleType.RAPID_BOOKING_CREATION,
            severity=RiskLevel.MEDIUM,
            score_impact=20.0,
            thresholds={"max_bookings_per_hour": 5},
            is_active=True,
        ),
        FraudRule.model_construct(
            rule_key="suspicious_api_patterns",
            name="Anomalous API Traffic Bursts",
            description="Detects API bursts",
            rule_type=FraudRuleType.SUSPICIOUS_API_PATTERNS,
            severity=RiskLevel.CRITICAL,
            score_impact=35.0,
            thresholds={"max_rpm": 120},
            is_active=True,
        ),
    ]

    activity = {
        "bookings_count_1h": 7,
        "api_requests_per_minute": 150,
    }

    triggered = FraudRuleEngine.evaluate_rules(activity, rules)
    assert len(triggered) == 2
    keys = [t.rule_key for t in triggered]
    assert "rapid_booking_creation" in keys
    assert "suspicious_api_patterns" in keys


def test_risk_assessment_scoring():
    """Verify RiskAssessmentService scoring and action recommendations."""
    # Low Risk (Score < 40)
    score_low, level_low, reason_low, action_low = RiskAssessmentService.evaluate_risk([])
    assert score_low == 0.0
    assert level_low == RiskLevel.LOW
    assert action_low == AutomatedAction.WARNING

    # High Risk (Score >= 60)
    mock_triggered = [
        TriggeredRuleDetail(
            rule_key="r1",
            name="Rule 1",
            rule_type=FraudRuleType.MULTIPLE_FAILED_LOGINS,
            severity=RiskLevel.HIGH,
            score_impact=35.0,
            reason="Triggered r1",
        ),
        TriggeredRuleDetail(
            rule_key="r2",
            name="Rule 2",
            rule_type=FraudRuleType.SUSPICIOUS_QUOTATION_ACTIVITY,
            severity=RiskLevel.HIGH,
            score_impact=30.0,
            reason="Triggered r2",
        ),
    ]
    score_high, level_high, reason_high, action_high = RiskAssessmentService.evaluate_risk(mock_triggered)
    assert score_high == 65.0
    assert level_high == RiskLevel.HIGH
    assert action_high == AutomatedAction.TEMPORARY_RESTRICTION


@pytest.mark.asyncio
async def test_fraud_detection_service_analyze_activity():
    """Test FraudDetectionService analyzing activity payload."""
    req = FraudAnalysisRequest(
        user_id="user_fraud_123",
        event_type="login_attempt",
        activity_data={"failed_logins": 7},
    )

    real_rule = FraudRule.model_construct(
        rule_key="multiple_failed_logins",
        name="Multiple Failed Login Attempts",
        description="Detects excessive failed logins",
        rule_type=FraudRuleType.MULTIPLE_FAILED_LOGINS,
        severity=RiskLevel.HIGH,
        score_impact=25.0,
        thresholds={"max_attempts": 5},
        is_active=True,
    )

    fake_event = FraudEvent.model_construct(event_id="fevt_100")

    with patch("app.fraud.service.FraudConfigService.list_active_rules", new_callable=AsyncMock, return_value=[real_rule]), \
         patch("app.fraud.repository.FraudEventRepository.create_event", new_callable=AsyncMock, return_value=fake_event), \
         patch("app.fraud.service.AlertService.generate_alert", new_callable=AsyncMock), \
         patch("app.trust.service.RiskService.record_risk_event", new_callable=AsyncMock), \
         patch("app.trust.repository.TrustProfileRepository.get_by_user_id", new_callable=AsyncMock, return_value=None), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        resp = await FraudDetectionService.analyze_activity(req)

        assert resp.user_id == "user_fraud_123"
        assert resp.risk_score == 25.0
        assert len(resp.triggered_rules) == 1
        assert resp.event_id == "fevt_100"
