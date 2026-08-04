"""
Unit tests for Trust & Safety Infrastructure services, repositories, and engine.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

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
from app.utils.enums import UserRole


# ---------------------------------------------------------------------------
# Trust Score Engine Tests
# ---------------------------------------------------------------------------

def test_trust_score_engine_thresholds():
    """Verify trust score mapping to TrustLevel categories."""
    assert TrustScoreEngine.calculate_trust_level(95.0) == TrustLevel.EXCELLENT
    assert TrustScoreEngine.calculate_trust_level(90.0) == TrustLevel.EXCELLENT
    assert TrustScoreEngine.calculate_trust_level(85.0) == TrustLevel.TRUSTED
    assert TrustScoreEngine.calculate_trust_level(75.0) == TrustLevel.TRUSTED
    assert TrustScoreEngine.calculate_trust_level(60.0) == TrustLevel.STANDARD
    assert TrustScoreEngine.calculate_trust_level(40.0) == TrustLevel.WATCHLIST
    assert TrustScoreEngine.calculate_trust_level(20.0) == TrustLevel.HIGH_RISK
    assert TrustScoreEngine.calculate_trust_level(10.0) == TrustLevel.RESTRICTED
    assert TrustScoreEngine.calculate_trust_level(0.0) == TrustLevel.RESTRICTED


def test_trust_score_engine_custom_thresholds():
    """Verify trust score mapping with custom policy thresholds."""
    custom = {
        "excellent": 95.0,
        "trusted": 85.0,
        "standard": 70.0,
        "watchlist": 50.0,
        "high_risk": 30.0,
    }
    assert TrustScoreEngine.calculate_trust_level(90.0, custom) == TrustLevel.TRUSTED
    assert TrustScoreEngine.calculate_trust_level(96.0, custom) == TrustLevel.EXCELLENT
    assert TrustScoreEngine.calculate_trust_level(20.0, custom) == TrustLevel.RESTRICTED


# ---------------------------------------------------------------------------
# Immutability Guard Test
# ---------------------------------------------------------------------------

def test_audit_log_immutability():
    """Verify that TrustAuditLogRepository explicitly prevents updates and deletions."""
    from app.trust.repository import TrustAuditLogRepository

    with pytest.raises(RuntimeError, match="Audit logs are immutable"):
        TrustAuditLogRepository.update_audit_log()

    with pytest.raises(RuntimeError, match="Audit logs are immutable"):
        TrustAuditLogRepository.delete_audit_log()


# ---------------------------------------------------------------------------
# Service Async Tests (Mocked DB)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_trust_service_get_or_create_profile():
    """Test get_or_create_profile creating a default profile if none exists."""
    user_id = "test_user_123"
    role = UserRole.CUSTOMER

    with patch("app.trust.repository.TrustProfileRepository.get_by_user_id", new_callable=AsyncMock) as mock_get, \
         patch("app.trust.repository.TrustProfileRepository.create_profile", new_callable=AsyncMock) as mock_create, \
         patch("app.trust.service.ConfigService.get_score_thresholds", new_callable=AsyncMock) as mock_thresh, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit:

        mock_get.return_value = None
        mock_thresh.return_value = {
            "excellent": 90.0,
            "trusted": 75.0,
            "standard": 50.0,
            "watchlist": 30.0,
            "high_risk": 15.0,
        }
        mock_create.return_value = MagicMock(
            user_id=user_id,
            role=role,
            trust_score=75.0,
            trust_level=TrustLevel.TRUSTED,
        )

        profile = await TrustService.get_or_create_profile(user_id, role)

        assert profile.user_id == user_id
        mock_create.assert_called_once()
        mock_audit.assert_called_once()


@pytest.mark.asyncio
async def test_risk_service_record_event():
    """Test recording a risk event and triggering risk evaluation."""
    user_id = "user_risk_123"
    event_type = RiskEventType.SUSPICIOUS_ACTIVITY
    severity = RiskLevel.HIGH

    with patch("app.trust.repository.RiskEventRepository.create_risk_event", new_callable=AsyncMock) as mock_create, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock) as mock_audit, \
         patch("app.trust.service.RiskService.evaluate_user_risk_level", new_callable=AsyncMock) as mock_eval:

        mock_create.return_value = MagicMock(event_id="evt_123")

        event = await RiskService.record_risk_event(
            user_id=user_id,
            event_type=event_type,
            severity=severity,
            description="Suspicious login location detected",
        )

        assert event.event_id == "evt_123"
        mock_create.assert_called_once()
        mock_audit.assert_called_once()
        mock_eval.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_safety_event_manager_raise_and_resolve_flag():
    """Test raising and resolving a safety flag."""
    user_id = "user_flag_123"

    fake_flag = MagicMock(
        flag_id="flag_999",
        user_id=user_id,
        flag_type="Identity Ambiguity",
        status="active",
    )

    fake_profile = MagicMock(
        user_id=user_id,
        safety_flags=[],
        review_status=ReviewStatus.CLEAR,
    )

    with patch("app.trust.repository.SafetyFlagRepository.create_flag", new_callable=AsyncMock, return_value=fake_flag), \
         patch("app.trust.repository.TrustProfileRepository.get_by_user_id", new_callable=AsyncMock, return_value=fake_profile), \
         patch("app.trust.repository.TrustProfileRepository.update_profile", new_callable=AsyncMock) as mock_update, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        flag = await SafetyEventManager.raise_safety_flag(
            user_id=user_id,
            flag_type="Identity Ambiguity",
            reason="Mismatched name details",
            severity=RiskLevel.MEDIUM,
        )

        assert flag.flag_id == "flag_999"
        mock_update.assert_called_once()
