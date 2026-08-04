"""
REST API endpoints for Referral & Rewards module.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep
from app.referral.schemas import (
    InviteRead,
    InviteRequest,
    LeaderboardEntryRead,
    ReferralApplyRequest,
    ReferralHistoryRead,
    ReferralStatusRead,
    RewardHistoryRead,
    RewardOverviewRead,
)
from app.referral.service import ReferralService, RewardService

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. Referral Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/referrals/invite",
    response_model=InviteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Invite friends",
    description="Send a referral invitation to a friend via email or phone.",
)
async def send_invite(
    current_user: ActiveUserDep,
    req: InviteRequest,
) -> InviteRead:
    """Send referral invite."""
    return await ReferralService.send_invite(user_id=str(current_user.id), req=req)


@router.get(
    "/referrals/history",
    response_model=ReferralHistoryRead,
    summary="Get referral history",
    description="Retrieve history of referral invitations sent by current user.",
)
async def get_referral_history(
    current_user: ActiveUserDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ReferralHistoryRead:
    """Get referral history."""
    return await ReferralService.get_referral_history(
        user_id=str(current_user.id), skip=skip, limit=limit
    )


@router.get(
    "/referrals/status",
    response_model=ReferralStatusRead,
    summary="Get referral status",
    description="Retrieve user's unique referral code, share link, invite stats, points, and achievement badges.",
)
async def get_referral_status(current_user: ActiveUserDep) -> ReferralStatusRead:
    """Get referral status."""
    return await ReferralService.get_referral_status(str(current_user.id))


@router.post(
    "/referrals/apply",
    response_model=InviteRead,
    status_code=status.HTTP_200_OK,
    summary="Apply referral code",
    description="Apply a friend's referral code to current user account.",
)
async def apply_referral_code(
    current_user: ActiveUserDep,
    req: ReferralApplyRequest,
) -> InviteRead:
    """Apply referral code."""
    return await ReferralService.apply_referral_code(
        referred_user_id=str(current_user.id), referral_code=req.referral_code
    )


@router.get(
    "/referrals/leaderboard",
    response_model=list[LeaderboardEntryRead],
    summary="Get referral leaderboard",
    description="Retrieve future-ready platform top referrers ranking.",
)
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=50),
) -> list[LeaderboardEntryRead]:
    """Get referral leaderboard."""
    return await ReferralService.get_leaderboard(limit=limit)


# ---------------------------------------------------------------------------
# 2. Rewards Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/rewards",
    response_model=RewardOverviewRead,
    summary="Get rewards overview",
    description="Retrieve user's active reward points balance, lifetime points, badges, and available discount redemption tiers.",
)
async def get_rewards(current_user: ActiveUserDep) -> RewardOverviewRead:
    """Get rewards overview."""
    return await RewardService.get_rewards_overview(str(current_user.id))


@router.get(
    "/rewards/history",
    response_model=RewardHistoryRead,
    summary="Get reward point ledger history",
    description="Retrieve history of earned and redeemed reward points.",
)
async def get_rewards_history(
    current_user: ActiveUserDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> RewardHistoryRead:
    """Get reward history."""
    return await RewardService.get_rewards_history(
        user_id=str(current_user.id), skip=skip, limit=limit
    )
