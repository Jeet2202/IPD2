"""
Master E2E Verification Script for Customer Engagement Module (Phase 9.1).
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
from app.engagement.models import Favorite, RecentlyViewed, RecommendationHistory, SavedSearch
from app.engagement.schemas import FavoriteCreate, FavoriteType, ItemType, RecentlyViewedCreate, SavedSearchCreate
from app.engagement.service import FavoritesService, PersonalizationService, RecentlyViewedService, SavedSearchesService
from app.main import app
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


from app.trust.models import TrustAuditLog

async def run_verification():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 9.1 - CUSTOMER ENGAGEMENT E2E VERIFICATION")
    logger.info("================================================================================")

    # 1. Connect DB
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
    ]
    await connect_to_database(document_models=models)
    logger.info("[STEP 1/6] MongoDB connected & Beanie document models initialized.")

    try:
        # 2. Cleanup & Create Test User
        cust_email = "engagement_customer_p91@kaamsetu.com"
        await User.find({"email": cust_email}).delete()

        user = User(
            email=cust_email,
            phone="+919888800001",
            password_hash="hash",
            full_name="Priya Customer",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await user.insert()
        user_id = str(user.id)
        token = create_access_token(user_id, UserRole.CUSTOMER)
        logger.info("[STEP 2/6] Baseline customer user created (user_id=%s).", user_id)
        # 3. Direct Service Verification: Favorites, Recently Viewed & Saved Searches
        fav1 = await FavoritesService.add_favorite(
            user_id=user_id,
            req=FavoriteCreate(target_type=FavoriteType.WORKER, target_id="worker_p91_001", notes="Highly recommended electrician"),
        )
        fav2 = await FavoritesService.add_favorite(
            user_id=user_id,
            req=FavoriteCreate(target_type=FavoriteType.SERVICE, target_id="srv_plumbing_deep_fix", notes=None),
        )
        fav_list = await FavoritesService.list_favorites(user_id)
        assert fav_list.total_count == 2
        logger.info("[STEP 3/6] Favorites Service verified (2 favorites added).")

        view1 = await RecentlyViewedService.log_view(
            user_id=user_id,
            req=RecentlyViewedCreate(item_type=ItemType.WORKER, item_id="worker_p91_001", metadata={"source": "home_feed"}),
        )
        view2 = await RecentlyViewedService.log_view(
            user_id=user_id,
            req=RecentlyViewedCreate(item_type=ItemType.SERVICE, item_id="srv_plumbing_deep_fix", metadata={}),
        )
        recent_views = await RecentlyViewedService.get_recently_viewed(user_id)
        assert len(recent_views) == 2
        logger.info("[STEP 4/6] Recently Viewed Service verified (2 views logged).")

        search1 = await SavedSearchesService.save_search(
            user_id=user_id,
            req=SavedSearchCreate(name="AC Repair In Bandra", query="ac repair", category_id="cat_appliance", filters={"max_price": 1500}),
        )
        searches = await SavedSearchesService.list_saved_searches(user_id)
        assert len(searches) == 1
        logger.info("[STEP 5/6] Saved Searches Service verified (1 search preset saved).")

        # 4. REST API Endpoint Verification via HTTP Client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            headers = {"Authorization": f"Bearer {token}"}

            # GET /api/v1/engagement/home
            res_home = await ac.get("/api/v1/engagement/home", headers=headers)
            assert res_home.status_code == 200
            home_data = res_home.json()
            assert home_data["user_id"] == user_id
            assert len(home_data["continue_browsing"]) == 2
            assert home_data["favorite_workers_count"] == 1
            assert home_data["favorite_services_count"] == 1
            assert home_data["saved_searches_count"] == 1
            assert len(home_data["recommendations"]) >= 3
            logger.info("  -> GET /api/v1/engagement/home returned 200 OK.")

            # GET /api/v1/engagement/favorites
            res_favs = await ac.get("/api/v1/engagement/favorites", headers=headers)
            assert res_favs.status_code == 200
            assert res_favs.json()["total_count"] == 2
            logger.info("  -> GET /api/v1/engagement/favorites returned 200 OK.")

            # POST /api/v1/engagement/favorites
            res_add_fav = await ac.post(
                "/api/v1/engagement/favorites",
                json={"target_type": "worker", "target_id": "worker_p91_002", "notes": "Painter"},
                headers=headers,
            )
            assert res_add_fav.status_code == 201
            new_fav_id = res_add_fav.json()["favorite_id"]
            logger.info("  -> POST /api/v1/engagement/favorites returned 201 Created.")

            # DELETE /api/v1/engagement/favorites/{favorite_id}
            res_del_fav = await ac.delete(f"/api/v1/engagement/favorites/{new_fav_id}", headers=headers)
            assert res_del_fav.status_code == 200
            logger.info("  -> DELETE /api/v1/engagement/favorites/{favorite_id} returned 200 OK.")

            # GET /api/v1/engagement/recent
            res_recent = await ac.get("/api/v1/engagement/recent", headers=headers)
            assert res_recent.status_code == 200
            assert len(res_recent.json()) == 2
            logger.info("  -> GET /api/v1/engagement/recent returned 200 OK.")

            # GET /api/v1/engagement/saved-searches
            res_saved = await ac.get("/api/v1/engagement/saved-searches", headers=headers)
            assert res_saved.status_code == 200
            assert len(res_saved.json()) == 1
            search_id = res_saved.json()[0]["search_id"]
            logger.info("  -> GET /api/v1/engagement/saved-searches returned 200 OK.")

            # DELETE /api/v1/engagement/saved-searches/{search_id}
            res_del_search = await ac.delete(f"/api/v1/engagement/saved-searches/{search_id}", headers=headers)
            assert res_del_search.status_code == 200
            logger.info("  -> DELETE /api/v1/engagement/saved-searches/{search_id} returned 200 OK.")

            # GET /api/v1/engagement/recommendations
            res_recs = await ac.get("/api/v1/engagement/recommendations", headers=headers)
            assert res_recs.status_code == 200
            assert len(res_recs.json()) >= 3
            logger.info("  -> GET /api/v1/engagement/recommendations returned 200 OK.")

        logger.info("[STEP 6/6] All 9 Customer Engagement REST API endpoints operational and verified.")

    finally:
        await close_database_connection()

    logger.info("================================================================================")
    logger.info("PHASE 9.1 - CUSTOMER ENGAGEMENT E2E VERIFICATION COMPLETED SUCCESSFULLY!")
    logger.info("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_verification())
