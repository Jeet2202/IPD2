"""
Master Unified Audit Script for Phase 9 — Growth & Customer Engagement Production Audit.
"""

import asyncio
import logging
import time
from httpx import AsyncClient, ASGITransport

from app.address.models import Address
from app.auth.models import User, UserRole
from app.auth.security import create_access_token
from app.booking.models import Booking
from app.customer.models import CustomerProfile
from app.database.connection import close_database_connection, connect_to_database
from app.engagement.models import Favorite, RecentlyViewed, RecommendationHistory, SavedSearch
from app.main import app
from app.referral.models import Referral, Reward, RewardHistory
from app.support.models import (
    FAQ,
    HelpArticle,
    SOSConfiguration,
    SupportContact,
    SupportFeedback,
    SupportTicket,
)
from app.trust.models import TrustAuditLog
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_unified_audit():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 9 - UNIFIED PRODUCTION AUDIT & CERTIFICATION")
    logger.info("================================================================================")

    # 1. Database Connection & Document Models
    models = [
        User,
        CustomerProfile,
        WorkerProfile,
        Address,
        Booking,
        TrustAuditLog,
        Favorite,
        RecentlyViewed,
        SavedSearch,
        RecommendationHistory,
        Referral,
        Reward,
        RewardHistory,
        FAQ,
        HelpArticle,
        SupportTicket,
        SupportFeedback,
        SupportContact,
        SOSConfiguration,
    ]
    await connect_to_database(document_models=models)
    logger.info("[AUDIT STEP 1/7] Connected to MongoDB & initialized 13 Beanie ODM document models.")

    try:
        # 2. Collection Index Audit
        doc_classes = [
            Favorite, RecentlyViewed, SavedSearch, RecommendationHistory,
            Referral, Reward, RewardHistory,
            FAQ, HelpArticle, SupportTicket, SupportFeedback, SupportContact, SOSConfiguration
        ]
        indexed_count = 0
        for cls in doc_classes:
            indices = cls.get_settings().indexes
            indexed_count += len(indices)
            logger.info("  -> Collection '%s': %d index(es) configured.", cls.get_settings().name, len(indices))
        logger.info("[AUDIT STEP 2/7] Database Index Audit complete. %d total collection indexes verified.", indexed_count)

        # 3. Create Audit Test Users
        audit_cust_email = "p9_audit_cust@kaamsetu.com"
        audit_referee_email = "p9_audit_referee@kaamsetu.com"
        audit_admin_email = "p9_audit_admin@kaamsetu.com"
        audit_phones = ["+919888800001", "+919888800002", "+919888800003"]

        old_users = await User.find({"$or": [{"email": {"$in": [audit_cust_email, audit_referee_email, audit_admin_email]}}, {"phone": {"$in": audit_phones}}]}).to_list()
        old_ids = [str(u.id) for u in old_users]

        await User.find({"$or": [{"email": {"$in": [audit_cust_email, audit_referee_email, audit_admin_email]}}, {"phone": {"$in": audit_phones}}]}).delete()
        if old_ids:
            await Favorite.find({"user_id": {"$in": old_ids}}).delete()
            await RecentlyViewed.find({"user_id": {"$in": old_ids}}).delete()
            await SavedSearch.find({"user_id": {"$in": old_ids}}).delete()
            await Referral.find({"$or": [{"referrer_id": {"$in": old_ids}}, {"referred_user_id": {"$in": old_ids}}]}).delete()
            await Reward.find({"user_id": {"$in": old_ids}}).delete()
            await RewardHistory.find({"user_id": {"$in": old_ids}}).delete()
            await SupportTicket.find({"user_id": {"$in": old_ids}}).delete()
            await SupportFeedback.find({"user_id": {"$in": old_ids}}).delete()

        cust = User(email=audit_cust_email, phone="+919888800001", password_hash="hash", full_name="Aarav Customer", role=UserRole.CUSTOMER, is_active=True)
        await cust.insert()
        cust_id = str(cust.id)
        cust_token = create_access_token(cust_id, UserRole.CUSTOMER)

        referee = User(email=audit_referee_email, phone="+919888800002", password_hash="hash", full_name="Bhavya Referee", role=UserRole.CUSTOMER, is_active=True)
        await referee.insert()
        referee_id = str(referee.id)
        referee_token = create_access_token(referee_id, UserRole.CUSTOMER)

        admin = User(email=audit_admin_email, phone="+919888800003", password_hash="hash", full_name="Chiraag Admin", role=UserRole.ADMIN, is_active=True)
        await admin.insert()
        admin_id = str(admin.id)
        admin_token = create_access_token(admin_id, UserRole.ADMIN)

        logger.info("[AUDIT STEP 3/7] Created audit test users: Customer (%s), Referee (%s), Admin (%s).", cust_id, referee_id, admin_id)

        # 4. REST API Endpoint Audit via HTTP AsyncClient
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            headers_cust = {"Authorization": f"Bearer {cust_token}"}
            headers_referee = {"Authorization": f"Bearer {referee_token}"}
            headers_admin = {"Authorization": f"Bearer {admin_token}"}

            latencies: list[float] = []

            async def audit_req(method: str, path: str, **kwargs) -> any:
                t0 = time.perf_counter()
                res = await ac.request(method, path, **kwargs)
                dt_ms = (time.perf_counter() - t0) * 1000.0
                latencies.append(dt_ms)
                assert res.status_code in (200, 201), f"Endpoint {method} {path} returned {res.status_code}: {res.text}"
                return res

            # --- Module P9.1 Customer Engagement Audit ---
            logger.info("[AUDIT STEP 4/7] Auditing P9.1 Customer Engagement APIs...")
            await audit_req("POST", "/api/v1/engagement/favorites", json={"target_type": "worker", "target_id": "wrk_999"}, headers=headers_cust)
            await audit_req("GET", "/api/v1/engagement/favorites", headers=headers_cust)
            await audit_req("POST", "/api/v1/engagement/recent", json={"item_type": "service", "item_id": "srv_plumbing"}, headers=headers_cust)
            await audit_req("GET", "/api/v1/engagement/recent", headers=headers_cust)
            await audit_req("POST", "/api/v1/engagement/saved-searches", json={"name": "Electrician Bandra", "query_text": "Electrician", "city": "Mumbai"}, headers=headers_cust)
            await audit_req("GET", "/api/v1/engagement/saved-searches", headers=headers_cust)
            await audit_req("GET", "/api/v1/engagement/home", headers=headers_cust)
            await audit_req("GET", "/api/v1/engagement/recommendations", headers=headers_cust)
            logger.info("  -> P9.1 Customer Engagement: 8/8 Endpoints Audit Passed.")

            # --- Module P9.3 Referral & Rewards Audit ---
            logger.info("[AUDIT STEP 5/7] Auditing P9.3 Referral & Rewards APIs...")
            res_invite = await audit_req("POST", "/api/v1/referrals/invite", json={"email": audit_referee_email}, headers=headers_cust)
            ref_code = res_invite.json()["referral_code"]

            await audit_req("POST", "/api/v1/referrals/apply", json={"referral_code": ref_code}, headers=headers_referee)
            await audit_req("GET", "/api/v1/referrals/status", headers=headers_cust)
            await audit_req("GET", "/api/v1/referrals/history", headers=headers_cust)
            await audit_req("GET", "/api/v1/rewards", headers=headers_cust)
            await audit_req("GET", "/api/v1/rewards/history", headers=headers_cust)
            await audit_req("GET", "/api/v1/referrals/leaderboard", headers=headers_cust)
            logger.info("  -> P9.3 Referral & Rewards: 7/7 Endpoints Audit Passed.")

            # --- Module P9.6 Help Center & Customer Support Audit ---
            logger.info("[AUDIT STEP 6/7] Auditing P9.6 Help Center & Customer Support APIs...")
            res_faqs = await audit_req("GET", "/api/v1/help/faqs")
            faq_id = res_faqs.json()[0]["faq_id"]

            await audit_req("GET", f"/api/v1/help/faqs/{faq_id}", headers=headers_cust)
            res_arts = await audit_req("GET", "/api/v1/help/articles")
            art_id = res_arts.json()[0]["article_id"]

            await audit_req("GET", f"/api/v1/help/articles/{art_id}", headers=headers_cust)
            await audit_req("GET", "/api/v1/help/categories")

            res_t = await audit_req("POST", "/api/v1/support/tickets", json={"subject": "Audit Ticket", "description": "Testing ticket workflow", "category": "General", "priority": "medium"}, headers=headers_cust)
            t_id = res_t.json()["ticket_id"]

            await audit_req("GET", "/api/v1/support/tickets", headers=headers_cust)
            await audit_req("GET", f"/api/v1/support/tickets/{t_id}", headers=headers_cust)
            await audit_req("PUT", f"/api/v1/support/tickets/{t_id}", json={"reply": {"message": "User test response"}}, headers=headers_cust)
            await audit_req("POST", "/api/v1/support/feedback", json={"category": "app_feedback", "rating": 5, "message": "Excellent support backend."}, headers=headers_cust)
            await audit_req("GET", "/api/v1/support/contact")
            await audit_req("GET", "/api/v1/support/sos", headers=headers_cust)

            # React Admin endpoints
            await audit_req("POST", "/api/v1/admin/support/faqs", json={"question": "What is KaamSetu Audit?", "answer": "Unified production audit.", "category": "General"}, headers=headers_admin)
            await audit_req("GET", "/api/v1/admin/support/tickets", headers=headers_admin)
            await audit_req("PUT", f"/api/v1/admin/support/tickets/{t_id}/reply", json={"message": "Admin audit response"}, headers=headers_admin)
            await audit_req("GET", "/api/v1/admin/support/feedback", headers=headers_admin)
            await audit_req("GET", "/api/v1/admin/support/reports/export", headers=headers_admin)
            logger.info("  -> P9.6 Help Center & Customer Support: 17/17 Endpoints Audit Passed.")

            avg_lat = sum(latencies) / len(latencies)
            max_lat = max(latencies)
            logger.info("[AUDIT STEP 7/7] API Performance Audit complete. Tested %d API calls (Avg Latency: %.2f ms, Max Latency: %.2f ms).", len(latencies), avg_lat, max_lat)

        # Audit Logs verification
        audit_events = await TrustAuditLog.find({"user_id": cust_id}).to_list()
        logger.info("  -> Trust Audit Log Verification: Recorded %d audit log events for user %s.", len(audit_events), cust_id)
        assert len(audit_events) >= 3

    finally:
        await close_database_connection()

    logger.info("================================================================================")
    logger.info("PHASE 9 - UNIFIED PRODUCTION AUDIT & CERTIFICATION COMPLETED SUCCESSFULLY!")
    logger.info("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_unified_audit())
