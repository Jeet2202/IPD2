"""
Unit tests for Referral & Rewards module (Phase 9.3).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.exceptions import BadRequestException, NotFoundException
from app.referral.schemas import (
    InviteRequest,
    ReferralStatus,
    RewardActionType,
)
from app.referral.service import ReferralService, RewardService


@pytest.mark.asyncio
async def test_send_invite_workflow():
    """Test sending referral invite and self-referral/duplicate prevention."""
    user_id = "user_referrer_123"
    now = datetime.now(timezone.utc)

    mock_user = MagicMock(id=user_id, email="referrer@kaamsetu.com", phone="+919888877777")
    mock_referral = MagicMock(
        id="65f1234567890abcdef12345",
        referral_id="ref_001",
        referrer_id=user_id,
        referred_user_id=None,
        referral_code="KSUSER_R",
        referee_email="friend@kaamsetu.com",
        referee_phone="+919888800002",
        status=ReferralStatus.INVITED,
        created_at=now,
        completed_at=None,
    )

    with patch("app.auth.models.User.get", new_callable=AsyncMock) as mock_get_user, \
         patch("app.referral.repository.ReferralRepository.get_pending_referral_for_contact", new_callable=AsyncMock) as mock_get_pending, \
         patch("app.referral.repository.ReferralRepository.create_referral", new_callable=AsyncMock) as mock_create, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        mock_get_user.return_value = mock_user
        mock_get_pending.return_value = None
        mock_create.return_value = mock_referral

        # 1. Successful Invite
        invite = await ReferralService.send_invite(
            user_id=user_id,
            req=InviteRequest(email="friend@kaamsetu.com", phone="+919888800002", notes="Join KaamSetu!"),
        )
        assert invite.referral_id == "ref_001"
        assert invite.status == ReferralStatus.INVITED

        # 2. Self Referral Error (Email match)
        with pytest.raises(BadRequestException) as exc1:
            await ReferralService.send_invite(
                user_id=user_id,
                req=InviteRequest(email="referrer@kaamsetu.com"),
            )
        assert "cannot send a referral invitation to yourself" in str(exc1.value)

        # 3. Duplicate Pending Invite Error
        mock_get_pending.return_value = mock_referral
        with pytest.raises(BadRequestException) as exc2:
            await ReferralService.send_invite(
                user_id=user_id,
                req=InviteRequest(email="friend@kaamsetu.com"),
            )
        assert "already sent an invite to this contact" in str(exc2.value)


@pytest.mark.asyncio
async def test_apply_referral_code_workflow():
    """Test applying a referral code to a new user."""
    referee_id = "user_referee_456"
    referrer_id = "user_referrer_123"
    now = datetime.now(timezone.utc)

    mock_referral = MagicMock(
        id="65f1234567890abcdef54321",
        referral_id="ref_002",
        referrer_id=referrer_id,
        referred_user_id=referee_id,
        referral_code="KSUSER_R",
        referee_email=None,
        referee_phone=None,
        status=ReferralStatus.REGISTERED,
        created_at=now,
        completed_at=None,
    )

    with patch("app.referral.repository.ReferralRepository.get_by_referee_user", new_callable=AsyncMock) as mock_by_referee, \
         patch("app.referral.repository.ReferralRepository.get_pending_invite_by_code", new_callable=AsyncMock) as mock_pending, \
         patch("app.auth.models.User.find_all") as mock_find_all, \
         patch("app.referral.repository.ReferralRepository.create_referral", new_callable=AsyncMock) as mock_create:

        mock_by_referee.side_effect = [None, mock_referral]
        mock_pending.return_value = None
        mock_find_all.return_value.to_list = AsyncMock(return_value=[MagicMock(id=referrer_id)])
        mock_create.return_value = mock_referral

        # Apply code
        applied = await ReferralService.apply_referral_code(referee_id, "KSUSER_R")
        assert applied.referrer_id == referrer_id
        assert applied.status == ReferralStatus.REGISTERED

        # Applying again returns existing record
        reapplied = await ReferralService.apply_referral_code(referee_id, "KSUSER_R")
        assert reapplied.referral_id == "ref_002"


@pytest.mark.asyncio
async def test_referral_completion_and_reward_assignment():
    """Test validating booking completion, point awarding, and badge evaluation."""
    referee_id = "user_referee_456"
    referrer_id = "user_referrer_123"

    mock_referral = MagicMock(
        referral_id="ref_003",
        referrer_id=referrer_id,
        referred_user_id=referee_id,
        status=ReferralStatus.REGISTERED,
        save=AsyncMock(),
    )

    mock_reward_obj = MagicMock(
        user_id=referrer_id,
        points_balance=500,
        lifetime_points=500,
        total_referrals_completed=0,
        badges=[],
        save=AsyncMock(),
    )

    with patch("app.referral.repository.ReferralRepository.get_by_referee_user", new_callable=AsyncMock, return_value=mock_referral), \
         patch("app.referral.repository.RewardRepository.get_or_create_by_user", new_callable=AsyncMock, return_value=mock_reward_obj), \
         patch("app.referral.repository.RewardRepository.save", new_callable=AsyncMock), \
         patch("app.referral.repository.RewardHistoryRepository.add_history", new_callable=AsyncMock), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        success = await ReferralService.validate_and_complete_referral(referee_id, booking_id="booking_999")
        assert success is True
        assert mock_referral.status == ReferralStatus.REWARDED
        assert mock_reward_obj.total_referrals_completed == 1
        assert "FIRST_INVITE" in mock_reward_obj.badges


@pytest.mark.asyncio
async def test_reward_overview_and_history():
    """Test fetching reward overview and point history."""
    user_id = "user_test_789"
    now = datetime.now(timezone.utc)

    mock_reward = MagicMock(
        user_id=user_id,
        points_balance=600,
        lifetime_points=600,
        total_referrals_completed=1,
        badges=["FIRST_INVITE"],
    )

    mock_history_item = MagicMock(
        id="65f1234567890abcdef99999",
        history_id="hist_001",
        user_id=user_id,
        referral_id="ref_003",
        action_type=RewardActionType.REFERRAL_BONUS,
        points=500,
        description="Earned 500 bonus points",
        created_at=now,
    )

    with patch("app.referral.repository.RewardRepository.get_or_create_by_user", new_callable=AsyncMock, return_value=mock_reward), \
         patch("app.referral.repository.RewardHistoryRepository.list_by_user", new_callable=AsyncMock, return_value=[mock_history_item]), \
         patch("app.referral.repository.RewardHistoryRepository.count_by_user", new_callable=AsyncMock, return_value=1):

        overview = await RewardService.get_rewards_overview(user_id)
        assert overview.points_balance == 600
        assert len(overview.available_redemptions) == 3

        history = await RewardService.get_rewards_history(user_id)
        assert history.total_count == 1
        assert history.history[0].points == 500
