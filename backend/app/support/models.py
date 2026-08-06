"""
Beanie ODM document models for Help Center & Customer Support module.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
import uuid

from beanie import Document, Indexed
from pydantic import Field

from app.support.schemas import (
    FeedbackCategory,
    TicketPriority,
    TicketStatus,
)


class FAQ(Document):
    """
    Frequently Asked Questions catalog.
    Collection: faqs
    """
    faq_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    category: Annotated[str, Indexed()]
    is_popular: bool = False
    view_count: int = 0
    related_faq_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    order: int = 0
    is_active: bool = True

    class Settings:
        name = "faqs"
        indexes = [
            [("category", 1), ("is_active", 1)],
            [("is_popular", 1), ("is_active", 1)],
        ]


class HelpArticle(Document):
    """
    Knowledge Base Help Articles and Troubleshooting Guides.
    Collection: help_articles
    """
    article_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    category: Annotated[str, Indexed()]
    target_role: Annotated[str, Indexed()] = "all"  # all, customer, worker
    view_count: int = 0
    video_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_published: bool = True

    class Settings:
        name = "help_articles"
        indexes = [
            [("category", 1), ("is_published", 1)],
            [("target_role", 1), ("is_published", 1)],
        ]


class SupportTicket(Document):
    """
    Customer and Worker Support Ticket threads.
    Collection: support_tickets
    """
    ticket_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: f"TICK-{uuid.uuid4().hex[:8].upper()}")
    user_id: Annotated[str, Indexed()]
    user_role: str = "customer"
    subject: str
    description: str
    category: str = "General"
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    responses: list[dict[str, Any]] = Field(default_factory=list)
    assigned_admin_id: str | None = None
    booking_id: str | None = None
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None

    class Settings:
        name = "support_tickets"
        indexes = [
            [("user_id", 1), ("status", 1)],
            [("status", 1), ("priority", 1)],
            [("created_at", -1)],
        ]


class SupportFeedback(Document):
    """
    User app feedback, bug reports, and feature suggestions.
    Collection: support_feedback
    """
    feedback_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Annotated[str, Indexed()]
    user_role: str = "customer"
    category: FeedbackCategory = FeedbackCategory.APP_FEEDBACK
    rating: int | None = None
    message: str
    attachments: list[str] = Field(default_factory=list)
    status: str = "new"  # new, reviewed, actioned
    created_at: Annotated[datetime, Indexed()] = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "support_feedback"
        indexes = [
            [("user_id", 1)],
            [("category", 1), ("status", 1)],
        ]


class SupportContact(Document):
    """
    Configurable platform contact details and business hours.
    Collection: support_contacts
    """
    contact_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str = "support@kaamsetu.com"
    phone: str = "+919579601589"
    whatsapp: str | None = "+919579601589"
    business_hours: str = "Monday - Saturday: 9:00 AM - 8:00 PM IST"
    address: str | None = "KaamSetu HQ, Bandra Kurla Complex, Mumbai, Maharashtra 400051"
    is_active: bool = True

    class Settings:
        name = "support_contacts"


class SOSConfiguration(Document):
    """
    Configurable emergency helpline numbers, guidelines, and safety info.
    Collection: sos_configuration
    """
    sos_id: Annotated[str, Indexed(unique=True)] = Field(default_factory=lambda: str(uuid.uuid4()))
    police_helpline: str = "112"
    women_helpline: str = "1091"
    ambulance_helpline: str = "108"
    kaamsetu_emergency_phone: str = "+91 1800-999-767"
    safety_guidelines: list[dict[str, str]] = Field(
        default_factory=lambda: [
            {"title": "Verify Worker Identity", "description": "Always check worker photo badge and OTP before granting entry."},
            {"title": "Share Job Tracking", "description": "Share real-time job status link with trusted emergency contacts."},
            {"title": "Emergency Escalation", "description": "Use the in-app SOS button to trigger immediate safety alerts."},
        ]
    )
    emergency_instructions: list[str] = Field(
        default_factory=lambda: [
            "Move to a safe, visible location if you feel unsafe.",
            "Call local law enforcement emergency number (112) immediately.",
            "Contact KaamSetu 24/7 Rapid Response Team via the helpline below.",
        ]
    )
    live_location_sharing_enabled: bool = True
    is_active: bool = True

    class Settings:
        name = "sos_configuration"
