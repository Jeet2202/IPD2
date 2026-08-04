"""
Database access repositories for Help Center & Customer Support module.
"""

from datetime import datetime, timezone
from typing import Any

from app.support.models import (
    FAQ,
    HelpArticle,
    SOSConfiguration,
    SupportContact,
    SupportFeedback,
    SupportTicket,
)
from app.support.schemas import TicketPriority, TicketStatus


class FAQRepository:
    """DB Repository for FAQs."""

    @staticmethod
    async def create_faq(data: dict[str, Any]) -> FAQ:
        """Create a new FAQ document."""
        faq = FAQ(**data)
        await faq.insert()
        return faq

    @staticmethod
    async def get_by_id(faq_id: str) -> FAQ | None:
        """Get FAQ by faq_id."""
        return await FAQ.find_one(FAQ.faq_id == str(faq_id))

    @staticmethod
    async def list_faqs(
        category: str | None = None,
        popular_only: bool = False,
        search_query: str | None = None,
        include_inactive: bool = False,
    ) -> list[FAQ]:
        """Fetch FAQs with category, popular, and text search filters."""
        query: dict[str, Any] = {}
        if not include_inactive:
            query["is_active"] = True
        if category:
            query["category"] = category
        if popular_only:
            query["is_popular"] = True

        faqs = await FAQ.find(query).sort("order").to_list()

        if search_query:
            q_lower = search_query.lower()
            faqs = [f for f in faqs if q_lower in f.question.lower() or q_lower in f.answer.lower() or any(q_lower in t.lower() for t in f.tags)]

        return faqs

    @staticmethod
    async def increment_view(faq: FAQ) -> None:
        """Increment view count for FAQ."""
        faq.view_count += 1
        await faq.save()

    @staticmethod
    async def update_faq(faq_id: str, updates: dict[str, Any]) -> FAQ | None:
        """Update FAQ by ID."""
        faq = await FAQRepository.get_by_id(faq_id)
        if not faq:
            return None
        for k, v in updates.items():
            if v is not None and hasattr(faq, k):
                setattr(faq, k, v)
        await faq.save()
        return faq

    @staticmethod
    async def delete_faq(faq_id: str) -> bool:
        """Soft-delete or delete FAQ by ID."""
        faq = await FAQRepository.get_by_id(faq_id)
        if faq:
            await faq.delete()
            return True
        return False


class HelpArticleRepository:
    """DB Repository for Knowledge Base Articles."""

    @staticmethod
    async def create_article(data: dict[str, Any]) -> HelpArticle:
        """Create a new HelpArticle document."""
        article = HelpArticle(**data)
        await article.insert()
        return article

    @staticmethod
    async def get_by_id(article_id: str) -> HelpArticle | None:
        """Get HelpArticle by article_id."""
        return await HelpArticle.find_one(HelpArticle.article_id == str(article_id))

    @staticmethod
    async def list_articles(
        category: str | None = None,
        role: str | None = None,
        search_query: str | None = None,
        include_unpublished: bool = False,
    ) -> list[HelpArticle]:
        """Fetch articles with category, role, and text search filters."""
        query: dict[str, Any] = {}
        if not include_unpublished:
            query["is_published"] = True
        if category:
            query["category"] = category

        articles = await HelpArticle.find(query).sort("-view_count").to_list()

        if role and role != "all":
            articles = [a for a in articles if a.target_role in ("all", role)]

        if search_query:
            q_lower = search_query.lower()
            articles = [a for a in articles if q_lower in a.title.lower() or q_lower in a.content.lower()]

        return articles

    @staticmethod
    async def increment_view(article: HelpArticle) -> None:
        """Increment view count for HelpArticle."""
        article.view_count += 1
        await article.save()

    @staticmethod
    async def update_article(article_id: str, updates: dict[str, Any]) -> HelpArticle | None:
        """Update HelpArticle by ID."""
        article = await HelpArticleRepository.get_by_id(article_id)
        if not article:
            return None
        for k, v in updates.items():
            if v is not None and hasattr(article, k):
                setattr(article, k, v)
        await article.save()
        return article

    @staticmethod
    async def delete_article(article_id: str) -> bool:
        """Delete HelpArticle by ID."""
        article = await HelpArticleRepository.get_by_id(article_id)
        if article:
            await article.delete()
            return True
        return False


class SupportTicketRepository:
    """DB Repository for Support Tickets."""

    @staticmethod
    async def create_ticket(data: dict[str, Any]) -> SupportTicket:
        """Create a new SupportTicket document."""
        ticket = SupportTicket(**data)
        await ticket.insert()
        return ticket

    @staticmethod
    async def get_by_id(ticket_id: str) -> SupportTicket | None:
        """Get ticket by ticket_id."""
        return await SupportTicket.find_one(SupportTicket.ticket_id == str(ticket_id))

    @staticmethod
    async def list_by_user(user_id: str, status: TicketStatus | None = None, skip: int = 0, limit: int = 50) -> list[SupportTicket]:
        """List tickets for a specific user."""
        query: dict[str, Any] = {"user_id": str(user_id)}
        if status:
            query["status"] = status
        return await SupportTicket.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_by_user(user_id: str, status: TicketStatus | None = None) -> int:
        """Count tickets for a specific user."""
        query: dict[str, Any] = {"user_id": str(user_id)}
        if status:
            query["status"] = status
        return await SupportTicket.find(query).count()

    @staticmethod
    async def list_all(
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SupportTicket]:
        """List all support tickets for admin dashboard."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if category:
            query["category"] = category
        return await SupportTicket.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_all(
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        category: str | None = None,
    ) -> int:
        """Count all support tickets for admin dashboard."""
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if priority:
            query["priority"] = priority
        if category:
            query["category"] = category
        return await SupportTicket.find(query).count()

    @staticmethod
    async def save(ticket: SupportTicket) -> SupportTicket:
        """Save updated ticket."""
        ticket.updated_at = datetime.now(timezone.utc)
        await ticket.save()
        return ticket


class SupportFeedbackRepository:
    """DB Repository for user feedback submissions."""

    @staticmethod
    async def create_feedback(data: dict[str, Any]) -> SupportFeedback:
        """Create a new SupportFeedback document."""
        fb = SupportFeedback(**data)
        await fb.insert()
        return fb

    @staticmethod
    async def list_feedback(category: str | None = None, status: str | None = None, skip: int = 0, limit: int = 50) -> list[SupportFeedback]:
        """List user feedback submissions for admin."""
        query: dict[str, Any] = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        return await SupportFeedback.find(query).sort("-created_at").skip(skip).limit(limit).to_list()

    @staticmethod
    async def count_feedback(category: str | None = None, status: str | None = None) -> int:
        """Count feedback entries."""
        query: dict[str, Any] = {}
        if category:
            query["category"] = category
        if status:
            query["status"] = status
        return await SupportFeedback.find(query).count()


class SupportContactRepository:
    """DB Repository for contact info."""

    @staticmethod
    async def get_active_contact() -> SupportContact:
        """Get or initialize default active contact information."""
        contact = await SupportContact.find_one(SupportContact.is_active == True)
        if not contact:
            contact = SupportContact()
            await contact.insert()
        return contact

    @staticmethod
    async def save(contact: SupportContact) -> SupportContact:
        """Save updated contact info."""
        await contact.save()
        return contact


class SOSConfigurationRepository:
    """DB Repository for SOS emergency configuration."""

    @staticmethod
    async def get_active_sos() -> SOSConfiguration:
        """Get or initialize default active SOS configuration."""
        sos = await SOSConfiguration.find_one(SOSConfiguration.is_active == True)
        if not sos:
            sos = SOSConfiguration()
            await sos.insert()
        return sos

    @staticmethod
    async def save(sos: SOSConfiguration) -> SOSConfiguration:
        """Save updated SOS configuration."""
        await sos.save()
        return sos
