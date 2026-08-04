"""
Database access repositories for Referral & Rewards module.
"""

from datetime import datetime, timezone
from typing import Any

from app.referral.models import Referral, Reward, RewardHistory
from app.referral.schemas import ReferralStatus


class ReferralRepository:
    """DB Repository for referral invitations and tracking."""

    @staticmethod
    async def create_referral(data: dict[str, Any]) -> Referral:
        """Create a new referral record."""
        ref = Referral(**data)
        await ref.insert()
        return ref

    @staticmethod
    async def get_by_id(referral_id: str) -> Referral | None:
        """Get referral by referral_id."""
        return await Referral.find_one(Referral.referral_id == str(referral_id))

    @staticmethod
    async def get_by_referee_user(referred_user_id: str) -> Referral | None:
        """Find referral associated with a registered referee."""
        return await Referral.find_one(Referral.referred_user_id == str(referred_user_id))

    @staticmethod
    async def get_by_code(referral_code: str) -> list[Referral]:
        """Find referral records matching code."""
        return await Referral.find(Referral.referral_code == referral_code.upper()).to_list()

    @staticmethod
    async def get_pending_referral_for_contact(email: str | None, phone: str | None) -> Referral | None:
        """Find existing pending referral invite by email or phone."""
        if email:
            ref = await Referral.find_one(
                Referral.referee_email == email.lower(),
                Referral.status == ReferralStatus.INVITED,
            )
            if ref:
                return ref
        if phone:
            ref = await Referral.find_one(
                Referral.referee_phone == phone,
                Referral.status == ReferralStatus.INVITED,
            )
            if ref:
                return ref
        return None

    @staticmethod
    async def get_pending_invite_by_code(referral_code: str) -> Referral | None:
        """Find pending invitation record for a referral code."""
        return await Referral.find_one(
            Referral.referral_code == referral_code.upper(),
            Referral.status == ReferralStatus.INVITED,
        )

    @staticmethod
    async def list_by_referrer(referrer_id: str, skip: int = 0, limit: int = 50) -> list[Referral]:
        """List all referral records for a referrer user."""
        return await Referral.find(Referral.referrer_id == str(referrer_id)).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_by_referrer(referrer_id: str, status: ReferralStatus | None = None) -> int:
        """Count referrals for a referrer user."""
        query: dict[str, Any] = {"referrer_id": str(referrer_id)}
        if status:
            query["status"] = status
        return await Referral.find(query).count()


class RewardRepository:
    """DB Repository for user reward balances and achievement badges."""

    @staticmethod
    async def get_or_create_by_user(user_id: str) -> Reward:
        """Get existing user reward document or initialize a new one."""
        user_id_str = str(user_id)
        reward = await Reward.find_one(Reward.user_id == user_id_str)
        if not reward:
            reward = Reward(user_id=user_id_str, points_balance=0, lifetime_points=0, total_referrals_completed=0, badges=[])
            await reward.insert()
        return reward

    @staticmethod
    async def save(reward: Reward) -> Reward:
        """Save updated reward document."""
        reward.updated_at = datetime.now(timezone.utc)
        await reward.save()
        return reward

    @staticmethod
    async def get_top_referrers(limit: int = 10) -> list[Reward]:
        """Fetch top referrers ordered by total_referrals_completed and lifetime_points."""
        return await Reward.find().sort("-total_referrals_completed", "-lifetime_points").limit(limit).to_list()


class RewardHistoryRepository:
    """DB Repository for points transaction ledger."""

    @staticmethod
    async def add_history(data: dict[str, Any]) -> RewardHistory:
        """Create a new point ledger entry."""
        item = RewardHistory(**data)
        await item.insert()
        return item

    @staticmethod
    async def list_by_user(user_id: str, skip: int = 0, limit: int = 50) -> list[RewardHistory]:
        """List reward transaction history for a user."""
        return await RewardHistory.find(RewardHistory.user_id == str(user_id)).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Count reward transaction history records for a user."""
        return await RewardHistory.find(RewardHistory.user_id == str(user_id)).count()

    @staticmethod
    async def get_top_referrers(limit: int = 10) -> list[Reward]:
        """Fetch top referrers ordered by total_referrals_completed and lifetime_points."""
        return await Reward.find().sort("-total_referrals_completed", "-lifetime_points").limit(limit).to_list()
