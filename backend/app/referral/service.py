"""
Domain services for Referral & Rewards module.
"""

from datetime import datetime, timezone
import logging
from typing import Any

from app.auth.models import User
from app.core.exceptions import BadRequestException, NotFoundException
from app.referral.models import Referral, Reward
from app.referral.repository import (
    ReferralRepository,
    RewardRepository,
    RewardHistoryRepository,
)
from app.referral.schemas import (
    InviteRead,
    InviteRequest,
    LeaderboardEntryRead,
    ReferralHistoryRead,
    ReferralStatus,
    ReferralStatusRead,
    RewardActionType,
    RewardHistoryItemRead,
    RewardHistoryRead,
    RewardOverviewRead,
    RewardRedemptionOption,
)
from app.trust.schemas import AuditEventType
from app.trust.service import AuditService

logger = logging.getLogger(__name__)

# Standard redemption options (Configurable point thresholds)
AVAILABLE_REDEMPTIONS = [
    RewardRedemptionOption(
        code="DISCOUNT_50",
        title="₹50 Service Discount",
        required_points=500,
        discount_amount=50,
        description="Redeem 500 points for flat ₹50 off on any service booking.",
    ),
    RewardRedemptionOption(
        code="DISCOUNT_120",
        title="₹120 Super Discount",
        required_points=1000,
        discount_amount=120,
        description="Redeem 1,000 points for flat ₹120 off on any service booking.",
    ),
    RewardRedemptionOption(
        code="DISCOUNT_250",
        title="₹250 Mega Discount",
        required_points=2000,
        discount_amount=250,
        description="Redeem 2,000 points for flat ₹250 off on any service booking.",
    ),
]


# ---------------------------------------------------------------------------
# Reward Service
# ---------------------------------------------------------------------------

class RewardService:
    """Manages customer reward balances, ledger entries, and achievement badges."""

    @staticmethod
    async def get_rewards_overview(user_id: str) -> RewardOverviewRead:
        """Fetch reward points overview, active balance, and badges."""
        reward = await RewardRepository.get_or_create_by_user(user_id)
        return RewardOverviewRead(
            user_id=str(user_id),
            points_balance=reward.points_balance,
            lifetime_points=reward.lifetime_points,
            total_referrals_completed=reward.total_referrals_completed,
            badges=reward.badges,
            available_redemptions=AVAILABLE_REDEMPTIONS,
        )

    @staticmethod
    async def award_points(
        user_id: str,
        action_type: RewardActionType,
        points: int,
        description: str,
        referral_id: str | None = None,
    ) -> None:
        """Add reward points to user account and log ledger history."""
        user_id_str = str(user_id)
        reward = await RewardRepository.get_or_create_by_user(user_id_str)
        reward.points_balance += points
        if points > 0:
            reward.lifetime_points += points

        await RewardRepository.save(reward)

        await RewardHistoryRepository.add_history({
            "user_id": user_id_str,
            "referral_id": referral_id,
            "action_type": action_type,
            "points": points,
            "description": description,
        })

    @staticmethod
    async def evaluate_badges(user_id: str) -> list[str]:
        """Check referral thresholds and unlock milestone achievement badges."""
        user_id_str = str(user_id)
        reward = await RewardRepository.get_or_create_by_user(user_id_str)
        unlocked: list[str] = []

        # Badge Threshold Definitions
        thresholds = [
            (1, "FIRST_INVITE", 100, "Unlocked 'First Invite' Badge (+100 bonus points)"),
            (5, "COMMUNITY_STAR", 500, "Unlocked 'Community Star' Badge (+500 bonus points)"),
            (10, "TOP_REFERRER", 1000, "Unlocked 'Top Referrer' Badge (+1000 bonus points)"),
        ]

        for req_count, badge_name, bonus_pts, msg in thresholds:
            if reward.total_referrals_completed >= req_count and badge_name not in reward.badges:
                reward.badges.append(badge_name)
                unlocked.append(badge_name)
                reward.points_balance += bonus_pts
                reward.lifetime_points += bonus_pts
                await RewardHistoryRepository.add_history({
                    "user_id": user_id_str,
                    "action_type": RewardActionType.BADGE_UNLOCKED,
                    "points": bonus_pts,
                    "description": msg,
                })

        if unlocked:
            await RewardRepository.save(reward)
            logger.info("User %s unlocked new badges: %s", user_id_str, unlocked)

        return reward.badges

    @staticmethod
    async def get_rewards_history(user_id: str, skip: int = 0, limit: int = 50) -> RewardHistoryRead:
        """Fetch paginated reward history."""
        user_id_str = str(user_id)
        items = await RewardHistoryRepository.list_by_user(user_id_str, skip=skip, limit=limit)
        total = await RewardHistoryRepository.count_by_user(user_id_str)
        dtos = [RewardHistoryItemRead.model_validate(i) for i in items]
        return RewardHistoryRead(history=dtos, total_count=total)


# ---------------------------------------------------------------------------
# Referral Service
# ---------------------------------------------------------------------------

class ReferralService:
    """Manages referral code generation, invitations, validation, and completion."""

    @staticmethod
    def generate_code_for_user(user_id: str) -> str:
        """Generate clean, unique, deterministic uppercase referral code."""
        clean_id = str(user_id).replace("-", "").upper()
        return f"KS{clean_id[:6]}"

    @staticmethod
    async def get_referral_status(user_id: str) -> ReferralStatusRead:
        """Fetch current user's referral code, link, stats, and badges."""
        user_id_str = str(user_id)
        code = ReferralService.generate_code_for_user(user_id_str)

        total_invites = await ReferralRepository.count_by_referrer(user_id_str)
        reg_count = await ReferralRepository.count_by_referrer(user_id_str, status=ReferralStatus.REGISTERED)
        comp_count = await ReferralRepository.count_by_referrer(user_id_str, status=ReferralStatus.REWARDED)

        reward = await RewardRepository.get_or_create_by_user(user_id_str)

        return ReferralStatusRead(
            referral_code=code,
            share_link=f"https://kaamsetu.com/invite?code={code}",
            total_invites=total_invites,
            registered_count=reg_count,
            completed_count=comp_count,
            points_balance=reward.points_balance,
            lifetime_points=reward.lifetime_points,
            badges=reward.badges,
        )

    @staticmethod
    async def send_invite(user_id: str, req: InviteRequest) -> InviteRead:
        """Create and track a referral invite to a friend."""
        user_id_str = str(user_id)

        if not req.email and not req.phone:
            raise BadRequestException("Either email or phone must be provided to send an invitation.")

        # Self referral validation
        user = await User.get(user_id_str)
        if user:
            if req.email and user.email.lower() == req.email.lower():
                raise BadRequestException("You cannot send a referral invitation to yourself.")
            if req.phone and user.phone == req.phone:
                raise BadRequestException("You cannot send a referral invitation to yourself.")

        # Duplicate invite check
        existing = await ReferralRepository.get_pending_referral_for_contact(req.email, req.phone)
        if existing:
            if existing.referrer_id == user_id_str:
                raise BadRequestException(f"You have already sent an invite to this contact ({req.email or req.phone}).")
            else:
                raise BadRequestException("This contact has already received a pending referral invite from another user.")

        code = ReferralService.generate_code_for_user(user_id_str)

        referral = await ReferralRepository.create_referral({
            "referrer_id": user_id_str,
            "referral_code": code,
            "referee_email": req.email.lower() if req.email else None,
            "referee_phone": req.phone,
            "notes": req.notes,
            "status": ReferralStatus.INVITED,
        })

        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Sent referral invite using code [{code}] to {req.email or req.phone}",
            actor={"id": user_id_str, "role": "customer"},
            metadata={"referral_id": referral.referral_id, "referral_code": code},
        )

        return InviteRead.model_validate(referral)

    @staticmethod
    async def apply_referral_code(referred_user_id: str, referral_code: str) -> InviteRead:
        """Apply a referral code to a newly registered user."""
        user_id_str = str(referred_user_id)
        code_upper = referral_code.strip().upper()

        # 1. Check existing referral for this user
        existing_ref = await ReferralRepository.get_by_referee_user(user_id_str)
        if existing_ref:
            return InviteRead.model_validate(existing_ref)

        # 2. Check for pending invitation matching code
        ref_record = await ReferralRepository.get_pending_invite_by_code(code_upper)
        if ref_record and ref_record.referrer_id != user_id_str:
            ref_record.referred_user_id = user_id_str
            ref_record.status = ReferralStatus.REGISTERED
            await ref_record.save()
            logger.info("User %s registered via pending referral invite %s", user_id_str, ref_record.referral_id)
            return InviteRead.model_validate(ref_record)

        # 3. Lookup referrer matching code directly from users
        referrer_id = None
        all_users = await User.find_all().to_list()
        for u in all_users:
            if ReferralService.generate_code_for_user(str(u.id)) == code_upper:
                referrer_id = str(u.id)
                break

        if not referrer_id or referrer_id == user_id_str:
            if referrer_id == user_id_str:
                raise BadRequestException("You cannot apply your own referral code.")
            raise NotFoundException(f"Invalid referral code '{referral_code}'.")

        ref_record = await ReferralRepository.create_referral({
            "referrer_id": referrer_id,
            "referred_user_id": user_id_str,
            "referral_code": code_upper,
            "status": ReferralStatus.REGISTERED,
        })

        logger.info("User %s registered with referral code %s from referrer %s", user_id_str, code_upper, referrer_id)
        return InviteRead.model_validate(ref_record)

    @staticmethod
    async def validate_and_complete_referral(referred_user_id: str, booking_id: str | None = None) -> bool:
        """
        Validate and complete referral upon first successful booking.
        Assigns referrer bonus (+500 pts), referee welcome bonus (+100 pts), and evaluates badges.
        """
        user_id_str = str(referred_user_id)
        referral = await ReferralRepository.get_by_referee_user(user_id_str)

        if not referral or referral.status == ReferralStatus.REWARDED:
            return False

        # Mark referral completed
        now = datetime.now(timezone.utc)
        referral.status = ReferralStatus.REWARDED
        referral.completed_at = now
        await referral.save()

        referrer_id = referral.referrer_id

        # 1. Referrer Reward (+500 points)
        await RewardService.award_points(
            user_id=referrer_id,
            action_type=RewardActionType.REFERRAL_BONUS,
            points=500,
            description="Earned 500 bonus points for successful friend referral completion!",
            referral_id=referral.referral_id,
        )

        # Increment referrer completed count & evaluate badges
        referrer_reward = await RewardRepository.get_or_create_by_user(referrer_id)
        referrer_reward.total_referrals_completed += 1
        await RewardRepository.save(referrer_reward)
        await RewardService.evaluate_badges(referrer_id)

        # 2. Referee Welcome Reward (+100 points)
        await RewardService.award_points(
            user_id=user_id_str,
            action_type=RewardActionType.WELCOME_BONUS,
            points=100,
            description="Received 100 welcome bonus points for completing your first booking via referral!",
            referral_id=referral.referral_id,
        )

        # Log Audit Events
        await AuditService.log_event(
            user_id=referrer_id,
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Completed referral for user [{user_id_str}], awarded 500 reward points.",
            actor={"id": user_id_str, "role": "customer"},
            metadata={"referral_id": referral.referral_id, "booking_id": booking_id},
        )

        logger.info("Successfully validated & completed referral %s for referrer %s", referral.referral_id, referrer_id)
        return True

    @staticmethod
    async def get_referral_history(user_id: str, skip: int = 0, limit: int = 50) -> ReferralHistoryRead:
        """Fetch user's referral invitation history."""
        user_id_str = str(user_id)
        referrals = await ReferralRepository.list_by_referrer(user_id_str, skip=skip, limit=limit)
        total = await ReferralRepository.count_by_referrer(user_id_str)
        dtos = [InviteRead.model_validate(r) for r in referrals]
        return ReferralHistoryRead(referrals=dtos, total_count=total)

    @staticmethod
    async def get_leaderboard(limit: int = 10) -> list[LeaderboardEntryRead]:
        """Fetch platform referral leaderboard (Future Ready)."""
        top_rewards = await RewardRepository.get_top_referrers(limit=limit)
        leaderboard: list[LeaderboardEntryRead] = []

        for idx, r in enumerate(top_rewards, start=1):
            user = await User.get(r.user_id)
            user_name = user.full_name if user else f"User {r.user_id[:6]}"
            leaderboard.append(
                LeaderboardEntryRead(
                    rank=idx,
                    user_id=r.user_id,
                    user_name=user_name,
                    total_referrals=r.total_referrals_completed,
                    points_earned=r.lifetime_points,
                )
            )

        return leaderboard
