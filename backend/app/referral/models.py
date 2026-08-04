"""
Beanie ODM document models for Referral & Rewards module.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid

from beanie import Document, Indexed
from pydantic import Field

from app.referral.schemas import ReferralStatus, RewardActionType


class Referral(Document):
    """
    Tracks referral invitations sent by users and their lifecycle progress.
    Collection: referrals
    """
    referral_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    referrer_id: Annotated[str, Indexed()]
    referred_user_id: Annotated[str, Indexed()] | None = None
    referral_code: Annotated[str, Indexed()]
    referee_email: str | None = None
    referee_phone: str | None = None
    status: ReferralStatus = Field(default=ReferralStatus.INVITED)
    notes: str | None = None
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    class Settings:
        name = "referrals"
        indexes = [
            [("referrer_id", 1), ("created_at", -1)],
            [("referred_user_id", 1), ("status", 1)],
            [("referral_code", 1), ("status", 1)],
        ]


class Reward(Document):
    """
    Stores customer reward points balance, lifetime accumulation, and achievement badges.
    Collection: rewards
    """
    reward_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Annotated[str, Indexed(unique=True)]
    points_balance: int = 0
    lifetime_points: int = 0
    total_referrals_completed: int = 0
    badges: list[str] = Field(default_factory=list)
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "rewards"
        indexes = [
            [("user_id", 1)],
        ]


class RewardHistory(Document):
    """
    Ledger recording all points additions, redemptions, and badge bonuses.
    Collection: reward_history
    """
    history_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Annotated[str, Indexed()]
    referral_id: str | None = None
    action_type: RewardActionType
    points: int
    description: str
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reward_history"
        indexes = [
            [("user_id", 1), ("created_at", -1)],
        ]
