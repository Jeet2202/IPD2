"""
Master E2E Verification Script for Referral & Rewards Module (Phase 9.3).
"""

import asyncio
import logging
from httpx import AsyncClient, ASGITransport

from app.address.models import Address
from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.booking.models import Booking
from app.customer.models import CustomerProfile
from app.database.connection import close_database_connection, connect_to_database
from app.main import app
from app.referral.models import Referral, Reward, RewardHistory
from app.referral.schemas import InviteRequest, ReferralStatus, RewardActionType
from app.referral.service import ReferralService, RewardService
from app.trust.models import TrustAuditLog
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 9.3 - REFERRAL & REWARDS E2E VERIFICATION")
    logger.info("================================================================================")

    # 1. Connect DB
    models = [
        User,
        CustomerProfile,
        WorkerProfile,
        Address,
        Booking,
        TrustAuditLog,
        Referral,
        Reward,
        RewardHistory,
    ]
    await connect_to_database(document_models=models)
    logger.info("[STEP 1/6] MongoDB connected & Beanie document models initialized.")

    try:
        # 2. Cleanup & Create Test Users (Referrer and Referee)
        referrer_email = "referrer_p93@kaamsetu.com"
        referee_email = "referee_p93@kaamsetu.com"

        old_users = await User.find({"email": {"$in": [referrer_email, referee_email]}}).to_list()
        old_ids = [str(u.id) for u in old_users]

        await User.find({"email": {"$in": [referrer_email, referee_email]}}).delete()
        await Referral.find({"$or": [{"referee_email": {"$in": [referrer_email, referee_email]}}, {"referrer_id": {"$in": old_ids}}]}).delete()
        await Reward.find({"user_id": {"$in": old_ids}}).delete()
        await RewardHistory.find({"user_id": {"$in": old_ids}}).delete()

        referrer = User(
            email=referrer_email,
            phone="+919999900001",
            password_hash="hash",
            full_name="Aarav Referrer",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await referrer.insert()
        referrer_id = str(referrer.id)
        referrer_token = create_access_token(referrer_id, UserRole.CUSTOMER)

        referee = User(
            email=referee_email,
            phone="+919999900002",
            password_hash="hash",
            full_name="Bhavya Referee",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await referee.insert()
        referee_id = str(referee.id)
        referee_token = create_access_token(referee_id, UserRole.CUSTOMER)

        logger.info("[STEP 2/6] Baseline Referrer (id=%s) and Referee (id=%s) created.", referrer_id, referee_id)

        # 3. Direct Referral & Rewards Workflow Verification
        invite = await ReferralService.send_invite(
            user_id=referrer_id,
            req=InviteRequest(email=referee_email, notes="Join KaamSetu and get 100 points!"),
        )
        assert invite.status == ReferralStatus.INVITED
        code = invite.referral_code
        logger.info("[STEP 3/6] Referral invite created (code=%s).", code)

        applied = await ReferralService.apply_referral_code(referee_id, code)
        assert applied.status == ReferralStatus.REGISTERED
        logger.info("  -> Applied referral code for referee user.")

        completed = await ReferralService.validate_and_complete_referral(referee_id, booking_id="booking_p93_demo")
        assert completed is True
        logger.info("[STEP 4/6] Completed referral via booking completion; points & badges assigned.")

        referrer_reward = await RewardService.get_rewards_overview(referrer_id)
        referee_reward = await RewardService.get_rewards_overview(referee_id)

        # Referrer got +500 referral bonus + 100 badge bonus = 600 points total
        assert referrer_reward.total_referrals_completed == 1
        assert "FIRST_INVITE" in referrer_reward.badges
        assert referrer_reward.points_balance == 600
        # Referee got +100 welcome bonus
        assert referee_reward.points_balance == 100

        logger.info("[STEP 5/6] Reward balances verified (Referrer: %d pts + Badge, Referee: %d pts).", referrer_reward.points_balance, referee_reward.points_balance)

        # 4. REST API Endpoints Verification via HTTP Client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            headers_referrer = {"Authorization": f"Bearer {referrer_token}"}
            headers_referee = {"Authorization": f"Bearer {referee_token}"}

            # GET /api/v1/referrals/status
            res_status = await ac.get("/api/v1/referrals/status", headers=headers_referrer)
            assert res_status.status_code == 200
            status_data = res_status.json()
            assert status_data["referral_code"] == code
            assert status_data["completed_count"] == 1
            assert "FIRST_INVITE" in status_data["badges"]
            logger.info("  -> GET /api/v1/referrals/status returned 200 OK.")

            # GET /api/v1/referrals/history
            res_history = await ac.get("/api/v1/referrals/history", headers=headers_referrer)
            assert res_history.status_code == 200
            assert res_history.json()["total_count"] >= 1
            logger.info("  -> GET /api/v1/referrals/history returned 200 OK.")

            # GET /api/v1/rewards
            res_rewards = await ac.get("/api/v1/rewards", headers=headers_referrer)
            assert res_rewards.status_code == 200
            assert res_rewards.json()["points_balance"] == 600
            assert len(res_rewards.json()["available_redemptions"]) == 3
            logger.info("  -> GET /api/v1/rewards returned 200 OK.")

            # GET /api/v1/rewards/history
            res_r_hist = await ac.get("/api/v1/rewards/history", headers=headers_referrer)
            assert res_r_hist.status_code == 200
            assert res_r_hist.json()["total_count"] >= 2 # bonus + badge
            logger.info("  -> GET /api/v1/rewards/history returned 200 OK.")

            # GET /api/v1/referrals/leaderboard
            res_leader = await ac.get("/api/v1/referrals/leaderboard", headers=headers_referrer)
            assert res_leader.status_code == 200
            assert any(entry["user_id"] == referrer_id for entry in res_leader.json())
            logger.info("  -> GET /api/v1/referrals/leaderboard returned 200 OK.")

        logger.info("[STEP 6/6] All Referral & Rewards REST API endpoints operational and verified.")

    finally:
        await close_database_connection()

    logger.info("================================================================================")
    logger.info("PHASE 9.3 - REFERRAL & REWARDS E2E VERIFICATION COMPLETED SUCCESSFULLY!")
    logger.info("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_verification())
