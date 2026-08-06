"""
Domain services for Help Center & Customer Support module.
"""

from datetime import datetime, timezone
import logging
from typing import Any
import uuid

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.support.models import (
    FAQ,
    HelpArticle,
    SOSConfiguration,
    SupportContact,
    SupportFeedback,
    SupportTicket,
)
from app.support.repository import (
    FAQRepository,
    HelpArticleRepository,
    SOSConfigurationRepository,
    SupportContactRepository,
    SupportFeedbackRepository,
    SupportTicketRepository,
)
from app.support.schemas import (
    ContactInfoRead,
    ContactInfoUpdate,
    FAQCreate,
    FAQRead,
    FAQUpdate,
    FeedbackCreate,
    FeedbackRead,
    HelpArticleCreate,
    HelpArticleRead,
    HelpArticleUpdate,
    SOSConfigRead,
    SOSConfigUpdate,
    SupportCategoryListRead,
    SupportReportExport,
    TicketAttachment,
    TicketCreate,
    TicketMessage,
    TicketPriority,
    TicketRead,
    TicketReplyRequest,
    TicketStatus,
    TicketStatusUpdateRequest,
)
from app.trust.schemas import AuditEventType
from app.trust.service import AuditService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FAQ Service
# ---------------------------------------------------------------------------

class FAQService:
    """Manages Frequently Asked Questions content and search."""

    @staticmethod
    async def seed_default_faqs_if_empty() -> None:
        """Seed initial FAQ list if database collection is empty."""
        existing_faqs = await FAQRepository.list_faqs(include_inactive=True)
        if existing_faqs:
            for faq in existing_faqs:
                if "Audit" in faq.question or "Audit" in faq.answer or "SOS" in faq.question:
                    await faq.delete()
                    continue
                modified = False
                if "KaamSetu" in faq.question:
                    faq.question = faq.question.replace("KaamSetu", "Ally")
                    modified = True
                if "KaamSetu" in faq.answer:
                    faq.answer = faq.answer.replace("KaamSetu", "Ally")
                    modified = True
                if modified:
                    await faq.save()
            return

        default_faqs = [
            {
                "question": "How do I book a service on Ally?",
                "answer": "Open the Ally app, select a service category (e.g. Electrician, Plumber), choose an address, select date & time, and tap 'Confirm Booking'. You will be instantly matched with a verified local professional.",
                "category": "Booking",
                "is_popular": True,
                "tags": ["booking", "schedule", "create"],
                "order": 1,
            },
            {
                "question": "How are workers verified for safety?",
                "answer": "All workers undergo strict 4-step identity verification including Aadhaar ID validation, background verification, police clearance certificate check, and skill testing before receiving verified badges.",
                "category": "Safety",
                "is_popular": True,
                "tags": ["safety", "verification", "trust", "worker"],
                "order": 2,
            },
            {
                "question": "What payment methods are supported?",
                "answer": "Ally supports UPI (GPay, PhonePe, Paytm), Credit/Debit Cards, Net Banking, Ally Wallet points, and Cash on Completion.",
                "category": "Payment",
                "is_popular": True,
                "tags": ["payment", "upi", "cash", "wallet"],
                "order": 3,
            },
            {
                "question": "How do I cancel or reschedule a booking?",
                "answer": "Navigate to 'My Bookings', select your active booking, and tap 'Reschedule' or 'Cancel Booking'. Free cancellation is available up to 2 hours before the scheduled time slot.",
                "category": "Booking",
                "is_popular": False,
                "tags": ["cancel", "reschedule", "booking"],
                "order": 4,
            },
            {
                "question": "How can I register as a worker on Ally?",
                "answer": "Download the Ally Worker app, register your mobile number, submit your ID documents and skills certificates. Once our team approves your profile, you can start receiving job requests.",
                "category": "Worker",
                "is_popular": False,
                "tags": ["worker", "register", "join"],
                "order": 5,
            },
        ]

        for item in default_faqs:
            await FAQRepository.create_faq(item)

        logger.info("Seeded %d default FAQ items.", len(default_faqs))

    @staticmethod
    async def list_faqs(
        category: str | None = None,
        popular_only: bool = False,
        search_query: str | None = None,
    ) -> list[FAQRead]:
        """Fetch FAQs with search and category filters."""
        await FAQService.seed_default_faqs_if_empty()
        faqs = await FAQRepository.list_faqs(
            category=category, popular_only=popular_only, search_query=search_query
        )
        return [FAQRead.model_validate(f) for f in faqs]

    @staticmethod
    async def get_faq_by_id(faq_id: str, user_id: str | None = None) -> FAQRead:
        """Fetch individual FAQ details and increment view counter."""
        faq = await FAQRepository.get_by_id(faq_id)
        if not faq or not faq.is_active:
            raise NotFoundException(f"FAQ '{faq_id}' not found.")

        await FAQRepository.increment_view(faq)

        if user_id:
            await AuditService.log_event(
                user_id=str(user_id),
                event_type=AuditEventType.PROFILE_UPDATES,
                description=f"Accessed FAQ [{faq.faq_id}]: '{faq.question}'",
                actor={"id": str(user_id), "role": "user"},
                metadata={"faq_id": faq.faq_id, "category": faq.category},
            )

        return FAQRead.model_validate(faq)

    @staticmethod
    async def create_faq(req: FAQCreate) -> FAQRead:
        """Create a new FAQ entry (Admin)."""
        faq = await FAQRepository.create_faq(req.model_dump())
        return FAQRead.model_validate(faq)

    @staticmethod
    async def update_faq(faq_id: str, req: FAQUpdate) -> FAQRead:
        """Update existing FAQ entry (Admin)."""
        faq = await FAQRepository.update_faq(faq_id=faq_id, updates=req.model_dump(exclude_none=True))
        if not faq:
            raise NotFoundException(f"FAQ '{faq_id}' not found.")
        return FAQRead.model_validate(faq)

    @staticmethod
    async def delete_faq(faq_id: str) -> bool:
        """Delete FAQ entry (Admin)."""
        success = await FAQRepository.delete_faq(faq_id)
        if not success:
            raise NotFoundException(f"FAQ '{faq_id}' not found.")
        return True


# ---------------------------------------------------------------------------
# Knowledge Base Service
# ---------------------------------------------------------------------------

class KnowledgeBaseService:
    """Manages Help Articles and Troubleshooting Guides."""

    @staticmethod
    async def seed_default_articles_if_empty() -> None:
        """Seed default Help Articles if help_articles collection is empty."""
        existing = await HelpArticleRepository.list_articles(include_unpublished=True)
        if existing:
            return

        default_articles = [
            {
                "title": "Complete Booking & Inspection Guide",
                "content": "# Complete Booking Guide\n\nLearn how to book skilled professionals for your home. You can choose immediate dispatch or scheduled visits. For complex renovation projects, request a site inspection visit first to receive an accurate line-item quotation.",
                "category": "Booking Help",
                "target_role": "all",
                "video_url": "https://www.youtube.com/watch?v=kaamsetu_booking_demo",
                "tags": ["booking", "inspection", "guide"],
            },
            {
                "title": "Account & Profile Management Guidelines",
                "content": "# Account & Profile Help\n\nKeep your personal details, service addresses, and contact numbers updated. Verify your phone and email to enable express single-tap bookings and seamless notification updates.",
                "category": "Account Help",
                "target_role": "all",
                "tags": ["account", "profile", "phone"],
            },
            {
                "title": "Worker Job Execution & Safety Manual",
                "content": "# Worker Safety & Service Execution\n\nAlways display your KaamSetu digital ID badge upon arrival. Perform site inspection before starting work, log pre-job inspection photos, and collect completion confirmation OTP from customer.",
                "category": "Worker Help",
                "target_role": "worker",
                "tags": ["worker", "safety", "otp"],
            },
        ]

        for item in default_articles:
            await HelpArticleRepository.create_article(item)

        logger.info("Seeded %d default Help Articles.", len(default_articles))

    @staticmethod
    async def list_articles(
        category: str | None = None,
        role: str | None = None,
        search_query: str | None = None,
    ) -> list[HelpArticleRead]:
        """Fetch help articles matching role and category."""
        await KnowledgeBaseService.seed_default_articles_if_empty()
        articles = await HelpArticleRepository.list_articles(
            category=category, role=role, search_query=search_query
        )
        return [HelpArticleRead.model_validate(a) for a in articles]

    @staticmethod
    async def get_article_by_id(article_id: str, user_id: str | None = None) -> HelpArticleRead:
        """Fetch article detail and increment view count."""
        article = await HelpArticleRepository.get_by_id(article_id)
        if not article or not article.is_published:
            raise NotFoundException(f"Help Article '{article_id}' not found.")

        await HelpArticleRepository.increment_view(article)

        if user_id:
            await AuditService.log_event(
                user_id=str(user_id),
                event_type=AuditEventType.PROFILE_UPDATES,
                description=f"Viewed Knowledge Base Article [{article.article_id}]: '{article.title}'",
                actor={"id": str(user_id), "role": "user"},
                metadata={"article_id": article.article_id, "category": article.category},
            )

        return HelpArticleRead.model_validate(article)

    @staticmethod
    async def create_article(req: HelpArticleCreate) -> HelpArticleRead:
        """Create new Help Article (Admin)."""
        article = await HelpArticleRepository.create_article(req.model_dump())
        return HelpArticleRead.model_validate(article)

    @staticmethod
    async def update_article(article_id: str, req: HelpArticleUpdate) -> HelpArticleRead:
        """Update Help Article (Admin)."""
        article = await HelpArticleRepository.update_article(article_id=article_id, updates=req.model_dump(exclude_none=True))
        if not article:
            raise NotFoundException(f"Help Article '{article_id}' not found.")
        return HelpArticleRead.model_validate(article)

    @staticmethod
    async def delete_article(article_id: str) -> bool:
        """Delete Help Article (Admin)."""
        success = await HelpArticleRepository.delete_article(article_id)
        if not success:
            raise NotFoundException(f"Help Article '{article_id}' not found.")
        return True


# ---------------------------------------------------------------------------
# Support Ticket Service
# ---------------------------------------------------------------------------

class SupportTicketService:
    """Manages support ticket creation, response threads, and resolution."""

    @staticmethod
    async def create_ticket(user_id: str, user_role: str, req: TicketCreate) -> TicketRead:
        """Create a new support ticket."""
        user_id_str = str(user_id)
        ticket = await SupportTicketRepository.create_ticket({
            "user_id": user_id_str,
            "user_role": user_role,
            "subject": req.subject,
            "description": req.description,
            "category": req.category,
            "priority": req.priority,
            "status": TicketStatus.OPEN,
            "attachments": [a.model_dump() for a in req.attachments],
            "booking_id": req.booking_id,
            "responses": [],
        })

        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Created support ticket [{ticket.ticket_id}] with subject '{req.subject}'",
            actor={"id": user_id_str, "role": user_role},
            metadata={"ticket_id": ticket.ticket_id, "priority": req.priority.value, "category": req.category},
        )

        return TicketRead.model_validate(ticket)

    @staticmethod
    async def list_user_tickets(user_id: str, status: TicketStatus | None = None, skip: int = 0, limit: int = 50) -> list[TicketRead]:
        """Fetch user's support tickets."""
        tickets = await SupportTicketRepository.list_by_user(user_id=str(user_id), status=status, skip=skip, limit=limit)
        return [TicketRead.model_validate(t) for t in tickets]

    @staticmethod
    async def get_user_ticket_by_id(user_id: str, ticket_id: str) -> TicketRead:
        """Get support ticket detail with ownership check."""
        ticket = await SupportTicketRepository.get_by_id(ticket_id)
        if not ticket or (ticket.user_id != str(user_id) and ticket.user_role != "admin"):
            raise NotFoundException(f"Support ticket '{ticket_id}' not found or access denied.")
        return TicketRead.model_validate(ticket)

    @staticmethod
    async def reply_to_ticket(user_id: str, user_role: str, ticket_id: str, req: TicketReplyRequest) -> TicketRead:
        """User or Admin posts a reply to ticket message thread."""
        ticket = await SupportTicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Support ticket '{ticket_id}' not found.")

        if user_role != "admin" and ticket.user_id != str(user_id):
            raise ForbiddenException("You are not authorized to reply to this ticket.")

        if ticket.status == TicketStatus.CLOSED:
            raise BadRequestException("Cannot reply to a closed ticket. Please reopen the ticket first.")

        now = datetime.now(timezone.utc)
        msg_obj = {
            "message_id": str(uuid.uuid4()),
            "sender_id": str(user_id),
            "sender_role": user_role,
            "message": req.message,
            "attachments": [a.model_dump() for a in req.attachments],
            "created_at": now,
        }

        ticket.responses.append(msg_obj)

        if user_role == "admin":
            ticket.status = TicketStatus.WAITING_FOR_USER
        else:
            ticket.status = TicketStatus.IN_PROGRESS if ticket.status != TicketStatus.OPEN else TicketStatus.OPEN

        await SupportTicketRepository.save(ticket)

        await AuditService.log_event(
            user_id=str(user_id),
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Replied to support ticket [{ticket.ticket_id}]",
            actor={"id": str(user_id), "role": user_role},
            metadata={"ticket_id": ticket.ticket_id, "sender_role": user_role},
        )

        return TicketRead.model_validate(ticket)

    @staticmethod
    async def update_ticket_status(user_id: str, user_role: str, ticket_id: str, req: TicketStatusUpdateRequest) -> TicketRead:
        """Update ticket status/priority/assigned admin."""
        ticket = await SupportTicketRepository.get_by_id(ticket_id)
        if not ticket:
            raise NotFoundException(f"Support ticket '{ticket_id}' not found.")

        if user_role != "admin" and ticket.user_id != str(user_id):
            raise ForbiddenException("You are not authorized to modify this ticket.")

        if req.status:
            ticket.status = req.status
            if req.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
                ticket.closed_at = datetime.now(timezone.utc)
        if req.priority and user_role == "admin":
            ticket.priority = req.priority
        if req.assigned_admin_id and user_role == "admin":
            ticket.assigned_admin_id = req.assigned_admin_id

        await SupportTicketRepository.save(ticket)
        return TicketRead.model_validate(ticket)


# ---------------------------------------------------------------------------
# Feedback, Contact & SOS Services
# ---------------------------------------------------------------------------

class FeedbackService:
    """Manages user feedback, bug reports, and feature requests."""

    @staticmethod
    async def submit_feedback(user_id: str, user_role: str, req: FeedbackCreate) -> FeedbackRead:
        """Submit feedback entry."""
        user_id_str = str(user_id)
        fb = await SupportFeedbackRepository.create_feedback({
            "user_id": user_id_str,
            "user_role": user_role,
            "category": req.category,
            "rating": req.rating,
            "message": req.message,
            "attachments": req.attachments,
            "status": "new",
        })

        await AuditService.log_event(
            user_id=user_id_str,
            event_type=AuditEventType.PROFILE_UPDATES,
            description=f"Submitted {req.category.value} feedback",
            actor={"id": user_id_str, "role": user_role},
            metadata={"feedback_id": fb.feedback_id, "category": req.category.value},
        )

        return FeedbackRead.model_validate(fb)

    @staticmethod
    async def list_feedback(category: str | None = None, status: str | None = None, skip: int = 0, limit: int = 50) -> list[FeedbackRead]:
        """List feedback submissions (Admin)."""
        items = await SupportFeedbackRepository.list_feedback(category=category, status=status, skip=skip, limit=limit)
        return [FeedbackRead.model_validate(i) for i in items]


class SupportContactService:
    """Delivers support contact details."""

    @staticmethod
    async def get_contact_info() -> ContactInfoRead:
        """Get active contact info."""
        contact = await SupportContactRepository.get_active_contact()
        return ContactInfoRead.model_validate(contact)

    @staticmethod
    async def update_contact_info(req: ContactInfoUpdate) -> ContactInfoRead:
        """Update contact info (Admin)."""
        contact = await SupportContactRepository.get_active_contact()
        for k, v in req.model_dump(exclude_none=True).items():
            if hasattr(contact, k):
                setattr(contact, k, v)
        await SupportContactRepository.save(contact)
        return ContactInfoRead.model_validate(contact)


class SOSService:
    """Delivers emergency SOS configuration and safety guidelines."""

    @staticmethod
    async def get_sos_config(user_id: str | None = None) -> SOSConfigRead:
        """Get active SOS configuration."""
        sos = await SOSConfigurationRepository.get_active_sos()

        if user_id:
            await AuditService.log_event(
                user_id=str(user_id),
                event_type=AuditEventType.PROFILE_UPDATES,
                description="Accessed SOS Emergency Information & Guidelines",
                actor={"id": str(user_id), "role": "user"},
                metadata={"sos_id": sos.sos_id},
            )

        return SOSConfigRead.model_validate(sos)

    @staticmethod
    async def update_sos_config(req: SOSConfigUpdate) -> SOSConfigRead:
        """Update SOS configuration (Admin)."""
        sos = await SOSConfigurationRepository.get_active_sos()
        updates = req.model_dump(exclude_none=True)
        for k, v in updates.items():
            if hasattr(sos, k):
                if k == "safety_guidelines" and isinstance(v, list):
                    setattr(sos, k, [g.model_dump() if hasattr(g, "model_dump") else g for g in v])
                else:
                    setattr(sos, k, v)
        await SOSConfigurationRepository.save(sos)
        return SOSConfigRead.model_validate(sos)


# ---------------------------------------------------------------------------
# Admin Support Management Service
# ---------------------------------------------------------------------------

class TicketManagementService:
    """Orchestrates administrative ticket management and reporting."""

    @staticmethod
    async def list_all_tickets(
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[TicketRead]:
        """Fetch all tickets for React Admin dashboard."""
        tickets = await SupportTicketRepository.list_all(
            status=status, priority=priority, category=category, skip=skip, limit=limit
        )
        return [TicketRead.model_validate(t) for t in tickets]

    @staticmethod
    async def get_support_categories() -> SupportCategoryListRead:
        """Fetch categories across FAQs, Knowledge Base, and Tickets."""
        await FAQService.seed_default_faqs_if_empty()
        await KnowledgeBaseService.seed_default_articles_if_empty()

        faqs = await FAQRepository.list_faqs(include_inactive=True)
        articles = await HelpArticleRepository.list_articles(include_unpublished=True)

        faq_cats = sorted(list(set(f.category for f in faqs)))
        article_cats = sorted(list(set(a.category for a in articles)))
        ticket_cats = ["Booking Issue", "Payment", "Technical", "Account", "Safety", "General"]

        return SupportCategoryListRead(
            faq_categories=faq_cats,
            article_categories=article_cats,
            ticket_categories=ticket_cats,
        )

    @staticmethod
    async def export_support_report() -> SupportReportExport:
        """Generate support summary report for React Admin."""
        all_tickets = await SupportTicketRepository.list_all(limit=1000)
        total = len(all_tickets)
        open_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.OPEN)
        in_prog_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.IN_PROGRESS)
        resolved_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.RESOLVED)
        closed_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.CLOSED)

        p_breakdown: dict[str, int] = {}
        c_breakdown: dict[str, int] = {}
        for t in all_tickets:
            p_val = t.priority.value if hasattr(t.priority, "value") else str(t.priority)
            p_breakdown[p_val] = p_breakdown.get(p_val, 0) + 1
            c_breakdown[t.category] = c_breakdown.get(t.category, 0) + 1

        total_fb = await SupportFeedbackRepository.count_feedback()

        return SupportReportExport(
            total_tickets=total,
            open_tickets=open_cnt,
            in_progress_tickets=in_prog_cnt,
            resolved_tickets=resolved_cnt,
            closed_tickets=closed_cnt,
            priority_breakdown=p_breakdown,
            category_breakdown=c_breakdown,
            total_feedback_submissions=total_fb,
            generated_at=datetime.now(timezone.utc),
        )
