"""
Unit tests for Help Center & Customer Support module (Phase 9.6).
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
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


@pytest.mark.asyncio
async def test_faq_and_knowledge_base_workflow():
    """Test searching FAQs, fetching category lists, and viewing help articles."""
    now = datetime.now(timezone.utc)
    mock_faq = MagicMock(
        id="65f1234567890abcdef11111",
        faq_id="faq_001",
        question="How do I book a service on KaamSetu?",
        answer="Select a category, choose address and confirm.",
        category="Booking",
        is_popular=True,
        view_count=5,
        related_faq_ids=[],
        tags=["booking"],
        order=1,
        is_active=True,
    )

    mock_article = MagicMock(
        id="65f1234567890abcdef22222",
        article_id="art_001",
        title="Complete Booking Guide",
        content="Guide content...",
        category="Booking Help",
        target_role="all",
        view_count=10,
        video_url=None,
        tags=["booking"],
        is_published=True,
    )

    with patch("app.support.repository.FAQRepository.list_faqs", new_callable=AsyncMock) as mock_list_faqs, \
         patch("app.support.repository.FAQRepository.get_by_id", new_callable=AsyncMock) as mock_get_faq, \
         patch("app.support.repository.FAQRepository.increment_view", new_callable=AsyncMock), \
         patch("app.support.repository.HelpArticleRepository.list_articles", new_callable=AsyncMock) as mock_list_arts, \
         patch("app.support.repository.HelpArticleRepository.get_by_id", new_callable=AsyncMock) as mock_get_art, \
         patch("app.support.repository.HelpArticleRepository.increment_view", new_callable=AsyncMock), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        mock_list_faqs.return_value = [mock_faq]
        mock_get_faq.return_value = mock_faq
        mock_list_arts.return_value = [mock_article]
        mock_get_art.return_value = mock_article

        # 1. List FAQs
        faqs = await FAQService.list_faqs(category="Booking", popular_only=True)
        assert len(faqs) == 1
        assert faqs[0].faq_id == "faq_001"

        # 2. Get FAQ details
        faq_detail = await FAQService.get_faq_by_id("faq_001", user_id="user_123")
        assert faq_detail.question == "How do I book a service on KaamSetu?"

        # 3. List Help Articles
        articles = await KnowledgeBaseService.list_articles(category="Booking Help", role="customer")
        assert len(articles) == 1
        assert articles[0].article_id == "art_001"

        # 4. Get Article details
        article_detail = await KnowledgeBaseService.get_article_by_id("art_001", user_id="user_123")
        assert article_detail.title == "Complete Booking Guide"


@pytest.mark.asyncio
async def test_support_ticket_lifecycle():
    """Test creating support ticket, thread replies, status transitions, and user history."""
    user_id = "cust_ticket_user_123"
    now = datetime.now(timezone.utc)

    mock_ticket = MagicMock(
        id="65f1234567890abcdef33333",
        ticket_id="TICK-00112233",
        user_id=user_id,
        user_role="customer",
        subject="Payment debited but booking unconfirmed",
        description="I was charged ₹500 via UPI but status is pending.",
        category="Payment",
        priority=TicketPriority.HIGH,
        status=TicketStatus.OPEN,
        attachments=[],
        responses=[],
        assigned_admin_id=None,
        booking_id="book_999",
        created_at=now,
        updated_at=now,
        closed_at=None,
    )

    with patch("app.support.repository.SupportTicketRepository.create_ticket", new_callable=AsyncMock) as mock_create, \
         patch("app.support.repository.SupportTicketRepository.list_by_user", new_callable=AsyncMock) as mock_list_user, \
         patch("app.support.repository.SupportTicketRepository.get_by_id", new_callable=AsyncMock) as mock_get, \
         patch("app.support.repository.SupportTicketRepository.save", new_callable=AsyncMock) as mock_save, \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        mock_create.return_value = mock_ticket
        mock_list_user.return_value = [mock_ticket]
        mock_get.return_value = mock_ticket

        # 1. Create Ticket
        ticket = await SupportTicketService.create_ticket(
            user_id=user_id,
            user_role="customer",
            req=TicketCreate(
                subject="Payment debited but booking unconfirmed",
                description="I was charged ₹500 via UPI but status is pending.",
                category="Payment",
                priority=TicketPriority.HIGH,
            ),
        )
        assert ticket.ticket_id == "TICK-00112233"
        assert ticket.priority == TicketPriority.HIGH

        # 2. List User Tickets
        user_tickets = await SupportTicketService.list_user_tickets(user_id)
        assert len(user_tickets) == 1

        # 3. User Reply to Ticket
        replied = await SupportTicketService.reply_to_ticket(
            user_id=user_id,
            user_role="customer",
            ticket_id="TICK-00112233",
            req=TicketReplyRequest(message="Here is my UPI transaction ref ID: 987654321"),
        )
        assert len(mock_ticket.responses) == 1

        # 4. Admin Reply & Status Transition
        admin_reply = await SupportTicketService.reply_to_ticket(
            user_id="admin_user_001",
            user_role="admin",
            ticket_id="TICK-00112233",
            req=TicketReplyRequest(message="We have verified your payment and confirmed your booking!"),
        )
        assert len(mock_ticket.responses) == 2
        assert mock_ticket.status == TicketStatus.WAITING_FOR_USER

        # 5. User Closes Ticket
        closed = await SupportTicketService.update_ticket_status(
            user_id=user_id,
            user_role="customer",
            ticket_id="TICK-00112233",
            req=TicketStatusUpdateRequest(status=TicketStatus.CLOSED),
        )
        assert mock_ticket.status == TicketStatus.CLOSED


@pytest.mark.asyncio
async def test_feedback_contact_and_sos():
    """Test submitting feedback, retrieving support contact info, and getting SOS emergency guidelines."""
    user_id = "test_feedback_user_456"
    now = datetime.now(timezone.utc)

    mock_feedback = MagicMock(
        id="65f1234567890abcdef44444",
        feedback_id="fb_001",
        user_id=user_id,
        user_role="customer",
        category=FeedbackCategory.APP_FEEDBACK,
        rating=5,
        message="Amazing app interface!",
        attachments=[],
        status="new",
        created_at=now,
    )

    mock_contact = MagicMock(
        contact_id="cnt_001",
        email="support@kaamsetu.com",
        phone="+91 1800-555-5226",
        whatsapp="+91 98765 43210",
        business_hours="Mon-Sat 9AM-8PM",
        address="Mumbai",
        is_active=True,
    )

    mock_sos = MagicMock(
        sos_id="sos_001",
        police_helpline="112",
        women_helpline="1091",
        ambulance_helpline="108",
        kaamsetu_emergency_phone="+91 1800-999-767",
        safety_guidelines=[{"title": "Verify OTP", "description": "Verify before entry."}],
        emergency_instructions=["Call 112."],
        live_location_sharing_enabled=True,
        is_active=True,
    )

    with patch("app.support.repository.SupportFeedbackRepository.create_feedback", new_callable=AsyncMock, return_value=mock_feedback), \
         patch("app.support.repository.SupportContactRepository.get_active_contact", new_callable=AsyncMock, return_value=mock_contact), \
         patch("app.support.repository.SOSConfigurationRepository.get_active_sos", new_callable=AsyncMock, return_value=mock_sos), \
         patch("app.trust.service.AuditService.log_event", new_callable=AsyncMock):

        # 1. Submit Feedback
        fb = await FeedbackService.submit_feedback(
            user_id=user_id,
            user_role="customer",
            req=FeedbackCreate(category=FeedbackCategory.APP_FEEDBACK, rating=5, message="Amazing app interface!"),
        )
        assert fb.feedback_id == "fb_001"

        # 2. Get Contact Info
        contact = await SupportContactService.get_contact_info()
        assert contact.email == "support@kaamsetu.com"

        # 3. Get SOS Info
        sos = await SOSService.get_sos_config(user_id=user_id)
        assert sos.police_helpline == "112"
        assert len(sos.safety_guidelines) == 1


@pytest.mark.asyncio
async def test_admin_support_management():
    """Test administrative management APIs: list all tickets, categories, and export support reports."""
    mock_ticket = MagicMock(
        id="65f1234567890abcdef55555",
        ticket_id="TICK-8888",
        user_id="user_123",
        user_role="customer",
        subject="Issue",
        description="Descr",
        category="General",
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.OPEN,
        attachments=[],
        responses=[],
        assigned_admin_id=None,
        booking_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        closed_at=None,
    )

    with patch("app.support.repository.SupportTicketRepository.list_all", new_callable=AsyncMock, return_value=[mock_ticket]), \
         patch("app.support.repository.SupportFeedbackRepository.count_feedback", new_callable=AsyncMock, return_value=5), \
         patch("app.support.repository.FAQRepository.list_faqs", new_callable=AsyncMock, return_value=[]), \
         patch("app.support.repository.HelpArticleRepository.list_articles", new_callable=AsyncMock, return_value=[]):

        tickets = await TicketManagementService.list_all_tickets(status=TicketStatus.OPEN)
        assert len(tickets) == 1

        report = await TicketManagementService.export_support_report()
        assert report.total_tickets == 1
        assert report.open_tickets == 1
        assert report.total_feedback_submissions == 5
