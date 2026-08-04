"""
Master E2E Verification Script for Help Center & Customer Support Module (Phase 9.6).
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
from app.support.models import (
    FAQ,
    HelpArticle,
    SOSConfiguration,
    SupportContact,
    SupportFeedback,
    SupportTicket,
)
from app.support.schemas import (
    FAQCreate,
    FeedbackCategory,
    FeedbackCreate,
    HelpArticleCreate,
    TicketCreate,
    TicketPriority,
    TicketReplyRequest,
    TicketStatus,
    TicketStatusUpdateRequest,
)
from app.support.service import (
    FAQService,
    FeedbackService,
    KnowledgeBaseService,
    SOSService,
    SupportContactService,
    SupportTicketService,
    TicketManagementService,
)
from app.trust.models import TrustAuditLog
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_verification():
    logger.info("================================================================================")
    logger.info("STARTING PHASE 9.6 - HELP CENTER & CUSTOMER SUPPORT E2E VERIFICATION")
    logger.info("================================================================================")

    # 1. Connect DB
    models = [
        User,
        CustomerProfile,
        WorkerProfile,
        Address,
        Booking,
        TrustAuditLog,
        FAQ,
        HelpArticle,
        SupportTicket,
        SupportFeedback,
        SupportContact,
        SOSConfiguration,
    ]
    await connect_to_database(document_models=models)
    logger.info("[STEP 1/6] MongoDB connected & Beanie document models initialized.")

    try:
        # 2. Cleanup & Create Test Users (Customer & Admin)
        cust_email = "support_cust_p96@kaamsetu.com"
        admin_email = "support_admin_p96@kaamsetu.com"

        old_users = await User.find({"email": {"$in": [cust_email, admin_email]}}).to_list()
        old_ids = [str(u.id) for u in old_users]

        await User.find({"email": {"$in": [cust_email, admin_email]}}).delete()
        if old_ids:
            await SupportTicket.find({"user_id": {"$in": old_ids}}).delete()
            await SupportFeedback.find({"user_id": {"$in": old_ids}}).delete()

        cust = User(
            email=cust_email,
            phone="+919777700001",
            password_hash="hash",
            full_name="Kavya Customer",
            role=UserRole.CUSTOMER,
            is_active=True,
        )
        await cust.insert()
        cust_id = str(cust.id)
        cust_token = create_access_token(cust_id, UserRole.CUSTOMER)

        admin = User(
            email=admin_email,
            phone="+919777700002",
            password_hash="hash",
            full_name="Aditya Support Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        await admin.insert()
        admin_id = str(admin.id)
        admin_token = create_access_token(admin_id, UserRole.ADMIN)

        logger.info("[STEP 2/6] Baseline Customer (id=%s) and Admin (id=%s) created.", cust_id, admin_id)

        # 3. Direct Service Verification: Seed content, FAQ & KB loading, SOS & Contact info
        faqs = await FAQService.list_faqs()
        assert len(faqs) >= 5
        logger.info("[STEP 3/6] FAQ Service verified (%d FAQs loaded/seeded).", len(faqs))

        articles = await KnowledgeBaseService.list_articles()
        assert len(articles) >= 3
        logger.info("  -> Knowledge Base Service verified (%d Articles loaded/seeded).", len(articles))

        contact = await SupportContactService.get_contact_info()
        assert contact.email == "support@kaamsetu.com"

        sos = await SOSService.get_sos_config(user_id=cust_id)
        assert sos.police_helpline == "112"
        logger.info("  -> Contact & SOS Services verified.")

        # 4. Ticket Lifecycle Service Verification
        ticket = await SupportTicketService.create_ticket(
            user_id=cust_id,
            user_role="customer",
            req=TicketCreate(
                subject="AC Service booking delayed",
                description="Worker has not arrived for scheduled 2 PM slot.",
                category="Booking Issue",
                priority=TicketPriority.HIGH,
            ),
        )
        assert ticket.status == TicketStatus.OPEN
        ticket_id = ticket.ticket_id
        logger.info("[STEP 4/6] Support Ticket created (id=%s, priority=%s).", ticket_id, ticket.priority.value)

        replied = await SupportTicketService.reply_to_ticket(
            user_id=cust_id, user_role="customer", ticket_id=ticket_id, req=TicketReplyRequest(message="Can you please assign another technician?")
        )
        assert len(replied.responses) == 1

        admin_replied = await SupportTicketService.reply_to_ticket(
            user_id=admin_id, user_role="admin", ticket_id=ticket_id, req=TicketReplyRequest(message="We have contacted worker and dispatched an alternate technician.")
        )
        assert len(admin_replied.responses) == 2
        assert admin_replied.status == TicketStatus.WAITING_FOR_USER
        logger.info("[STEP 5/6] Ticket thread replies and status transitions verified.")

        # 5. REST API Endpoints Verification via HTTP Client
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            headers_cust = {"Authorization": f"Bearer {cust_token}"}
            headers_admin = {"Authorization": f"Bearer {admin_token}"}

            # GET /api/v1/help/faqs
            res_faqs = await ac.get("/api/v1/help/faqs")
            assert res_faqs.status_code == 200
            assert len(res_faqs.json()) >= 5
            faq_0_id = res_faqs.json()[0]["faq_id"]
            logger.info("  -> GET /api/v1/help/faqs returned 200 OK.")

            # GET /api/v1/help/faqs/{id}
            res_faq_detail = await ac.get(f"/api/v1/help/faqs/{faq_0_id}", headers=headers_cust)
            assert res_faq_detail.status_code == 200
            logger.info("  -> GET /api/v1/help/faqs/{id} returned 200 OK.")

            # GET /api/v1/help/articles
            res_arts = await ac.get("/api/v1/help/articles")
            assert res_arts.status_code == 200
            art_0_id = res_arts.json()[0]["article_id"]
            logger.info("  -> GET /api/v1/help/articles returned 200 OK.")

            # GET /api/v1/help/articles/{id}
            res_art_detail = await ac.get(f"/api/v1/help/articles/{art_0_id}", headers=headers_cust)
            assert res_art_detail.status_code == 200
            logger.info("  -> GET /api/v1/help/articles/{id} returned 200 OK.")

            # GET /api/v1/help/categories
            res_cats = await ac.get("/api/v1/help/categories")
            assert res_cats.status_code == 200
            logger.info("  -> GET /api/v1/help/categories returned 200 OK.")

            # GET /api/v1/support/tickets
            res_user_tickets = await ac.get("/api/v1/support/tickets", headers=headers_cust)
            assert res_user_tickets.status_code == 200
            assert len(res_user_tickets.json()) >= 1
            logger.info("  -> GET /api/v1/support/tickets returned 200 OK.")

            # GET /api/v1/support/tickets/{id}
            res_t_detail = await ac.get(f"/api/v1/support/tickets/{ticket_id}", headers=headers_cust)
            assert res_t_detail.status_code == 200
            assert len(res_t_detail.json()["responses"]) == 2
            logger.info("  -> GET /api/v1/support/tickets/{id} returned 200 OK.")

            # POST /api/v1/support/feedback
            res_fb = await ac.post(
                "/api/v1/support/feedback",
                json={"category": "app_feedback", "rating": 5, "message": "Great Help Center implementation!"},
                headers=headers_cust,
            )
            assert res_fb.status_code == 201
            logger.info("  -> POST /api/v1/support/feedback returned 201 Created.")

            # GET /api/v1/support/contact
            res_contact = await ac.get("/api/v1/support/contact")
            assert res_contact.status_code == 200
            logger.info("  -> GET /api/v1/support/contact returned 200 OK.")

            # GET /api/v1/support/sos
            res_sos = await ac.get("/api/v1/support/sos", headers=headers_cust)
            assert res_sos.status_code == 200
            logger.info("  -> GET /api/v1/support/sos returned 200 OK.")

            # Admin Management APIs
            # POST /api/v1/admin/support/faqs
            res_admin_faq = await ac.post(
                "/api/v1/admin/support/faqs",
                json={"question": "What is KaamSetu SOS?", "answer": "SOS triggers safety emergency alerts.", "category": "Safety"},
                headers=headers_admin,
            )
            assert res_admin_faq.status_code == 201
            logger.info("  -> POST /api/v1/admin/support/faqs (React Admin) returned 201 Created.")

            # GET /api/v1/admin/support/tickets
            res_admin_tickets = await ac.get("/api/v1/admin/support/tickets", headers=headers_admin)
            assert res_admin_tickets.status_code == 200
            assert len(res_admin_tickets.json()) >= 1
            logger.info("  -> GET /api/v1/admin/support/tickets (React Admin) returned 200 OK.")

            # GET /api/v1/admin/support/reports/export
            res_admin_report = await ac.get("/api/v1/admin/support/reports/export", headers=headers_admin)
            assert res_admin_report.status_code == 200
            assert res_admin_report.json()["total_tickets"] >= 1
            logger.info("  -> GET /api/v1/admin/support/reports/export (React Admin) returned 200 OK.")

        logger.info("[STEP 6/6] All Help Center & Customer Support REST API endpoints operational and verified.")

    finally:
        await close_database_connection()

    logger.info("================================================================================")
    logger.info("PHASE 9.6 - HELP CENTER & CUSTOMER SUPPORT E2E VERIFICATION COMPLETED SUCCESSFULLY!")
    logger.info("================================================================================")


if __name__ == "__main__":
    asyncio.run(run_verification())
