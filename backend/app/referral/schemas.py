"""
Pydantic v2 schemas and Enums for Referral & Rewards module.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, EmailStr

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ReferralStatus(str, Enum):
    """Lifecycle status of a referral invitation."""
    INVITED = "invited"                 # Invite created / code shared
    REGISTERED = "registered"           # Friend registered account with referral code
    BOOKING_COMPLETED = "booking_completed" # Friend completed first booking
    REWARDED = "rewarded"               # Points and badges assigned to referrer and referee
    EXPIRED = "expired"                 # Referral invitation expired without completion


class RewardActionType(str, Enum):
    """Types of reward point transactions."""
    REFERRAL_BONUS = "referral_bonus"     # Points awarded to referrer for a successful referral
    WELCOME_BONUS = "welcome_bonus"       # Points awarded to referee upon first completed booking
    BADGE_UNLOCKED = "badge_unlocked"     # Bonus points for achieving a milestone badge
    POINTS_REDEEMED = "points_redeemed"   # Points redeemed for service discount
    PROMOTIONAL_CREDIT = "promotional_credit" # Administrative or promotional grant


# ---------------------------------------------------------------------------
# Invite & Referral DTOs
# ---------------------------------------------------------------------------

class InviteRequest(BaseModel):
    """Payload to send a referral invitation to a friend."""
    email: EmailStr | None = Field(default=None, description="Friend's email address")
    phone: str | None = Field(default=None, description="Friend's Indian phone number")
    notes: str | None = Field(default=None, max_length=200, description="Optional personal invitation message")


class InviteRead(BaseModel):
    """Read DTO for a referral record."""
    id: PyObjectId
    referral_id: str
    referrer_id: str
    referred_user_id: str | None = None
    referral_code: str
    referee_email: str | None = None
    referee_phone: str | None = None
    status: ReferralStatus
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReferralApplyRequest(BaseModel):
    """Payload to apply a referral code during registration or profile setup."""
    referral_code: str = Field(..., min_length=4, max_length=20, description="Unique referral code")


class ReferralStatusRead(BaseModel):
    """Current user's referral code, share URL, stats, and achievements."""
    referral_code: str
    share_link: str
    total_invites: int = 0
    registered_count: int = 0
    completed_count: int = 0
    points_balance: int = 0
    lifetime_points: int = 0
    badges: list[str] = Field(default_factory=list)


class ReferralHistoryRead(BaseModel):
    """Paginated list of user's referral invitations."""
    referrals: list[InviteRead]
    total_count: int


# ---------------------------------------------------------------------------
# Rewards & Leaderboard DTOs
# ---------------------------------------------------------------------------

class RewardRedemptionOption(BaseModel):
    """Available benefit tier for point redemption."""
    code: str
    title: str
    required_points: int
    discount_amount: int
    description: str


class RewardOverviewRead(BaseModel):
    """Overview of user's current points, badges, and available redemption options."""
    user_id: str
    points_balance: int = 0
    lifetime_points: int = 0
    total_referrals_completed: int = 0
    badges: list[str] = Field(default_factory=list)
    available_redemptions: list[RewardRedemptionOption] = Field(default_factory=list)


class RewardHistoryItemRead(BaseModel):
    """Individual reward point ledger transaction."""
    id: PyObjectId
    history_id: str
    user_id: str
    referral_id: str | None = None
    action_type: RewardActionType
    points: int
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RewardHistoryRead(BaseModel):
    """Paginated list of user's reward ledger transactions."""
    history: list[RewardHistoryItemRead]
    total_count: int


class LeaderboardEntryRead(BaseModel):
    """Leaderboard entry for top platform referrers (Future Ready)."""
    rank: int
    user_id: str
    user_name: str
    total_referrals: int
    points_earned: int
