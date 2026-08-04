"""
Pydantic v2 schemas and Enums for Help Center & Customer Support module.
"""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, EmailStr

PyObjectId = Annotated[str, BeforeValidator(str)]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TicketStatus(str, Enum):
    """Support ticket lifecycle status."""
    OPEN = "open"                     # Customer created ticket, awaiting support response
    IN_PROGRESS = "in_progress"         # Assigned to support admin, investigation underway
    WAITING_FOR_USER = "waiting_for_user" # Awaiting response/details from user
    RESOLVED = "resolved"             # Issue resolved by support team
    CLOSED = "closed"                 # Ticket closed permanently


class TicketPriority(str, Enum):
    """Urgency / Priority levels for support tickets."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackCategory(str, Enum):
    """Categories of user feedback submissions."""
    APP_FEEDBACK = "app_feedback"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL_SUGGESTION = "general_suggestion"


# ---------------------------------------------------------------------------
# FAQ DTOs
# ---------------------------------------------------------------------------

class FAQCreate(BaseModel):
    """Payload to create a new FAQ entry (Admin)."""
    question: str = Field(..., min_length=5, max_length=300)
    answer: str = Field(..., min_length=5)
    category: str = Field(..., max_length=50, description="Booking, Account, Payment, Worker, General")
    is_popular: bool = False
    related_faq_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    order: int = 0
    is_active: bool = True


class FAQUpdate(BaseModel):
    """Payload to update an existing FAQ entry (Admin)."""
    question: str | None = None
    answer: str | None = None
    category: str | None = None
    is_popular: bool | None = None
    related_faq_ids: list[str] | None = None
    tags: list[str] | None = None
    order: int | None = None
    is_active: bool | None = None


class FAQRead(BaseModel):
    """Read DTO for an FAQ entry."""
    id: PyObjectId
    faq_id: str
    question: str
    answer: str
    category: str
    is_popular: bool
    view_count: int
    related_faq_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Knowledge Base Article DTOs
# ---------------------------------------------------------------------------

class HelpArticleCreate(BaseModel):
    """Payload to create a new Knowledge Base Help Article (Admin)."""
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)
    category: str = Field(..., max_length=50)
    target_role: str = Field(default="all", description="all, customer, worker")
    video_url: str | None = Field(default=None, description="Optional tutorial video link")
    tags: list[str] = Field(default_factory=list)
    is_published: bool = True


class HelpArticleUpdate(BaseModel):
    """Payload to update a Knowledge Base Help Article (Admin)."""
    title: str | None = None
    content: str | None = None
    category: str | None = None
    target_role: str | None = None
    video_url: str | None = None
    tags: list[str] | None = None
    is_published: bool | None = None


class HelpArticleRead(BaseModel):
    """Read DTO for a Knowledge Base Help Article."""
    id: PyObjectId
    article_id: str
    title: str
    content: str
    category: str
    target_role: str
    view_count: int
    video_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_published: bool

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Support Ticket DTOs
# ---------------------------------------------------------------------------

class TicketAttachment(BaseModel):
    """Attachment document or image uploaded to Cloudinary."""
    url: str
    name: str = "attachment"
    size: int = 0
    type: str = "image"


class TicketMessage(BaseModel):
    """Individual message in a support ticket thread."""
    message_id: str
    sender_id: str
    sender_role: str
    message: str
    attachments: list[TicketAttachment] = Field(default_factory=list)
    created_at: datetime


class TicketCreate(BaseModel):
    """Payload to create a new Support Ticket."""
    subject: str = Field(..., min_length=5, max_length=150)
    description: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(default="General", description="Booking Issue, Payment, Technical, Account, Safety, General")
    priority: TicketPriority = Field(default=TicketPriority.MEDIUM)
    booking_id: str | None = Field(default=None, description="Optional associated booking ID")
    attachments: list[TicketAttachment] = Field(default_factory=list)


class TicketRead(BaseModel):
    """Read DTO for a Support Ticket."""
    id: PyObjectId
    ticket_id: str
    user_id: str
    user_role: str
    subject: str
    description: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    attachments: list[TicketAttachment] = Field(default_factory=list)
    responses: list[TicketMessage] = Field(default_factory=list)
    assigned_admin_id: str | None = None
    booking_id: str | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TicketReplyRequest(BaseModel):
    """Payload for user or admin to post a reply on a support ticket."""
    message: str = Field(..., min_length=2, max_length=2000)
    attachments: list[TicketAttachment] = Field(default_factory=list)


class TicketStatusUpdateRequest(BaseModel):
    """Payload for user or admin to update status, priority, or assigned admin."""
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_admin_id: str | None = None


# ---------------------------------------------------------------------------
# Feedback DTOs
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    """Payload to submit user app feedback or bug report."""
    category: FeedbackCategory
    rating: int | None = Field(default=None, ge=1, le=5)
    message: str = Field(..., min_length=5, max_length=1000)
    attachments: list[str] = Field(default_factory=list)


class FeedbackRead(BaseModel):
    """Read DTO for user feedback submission."""
    id: PyObjectId
    feedback_id: str
    user_id: str
    user_role: str
    category: FeedbackCategory
    rating: int | None = None
    message: str
    attachments: list[str] = Field(default_factory=list)
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Contact & SOS DTOs
# ---------------------------------------------------------------------------

class ContactInfoRead(BaseModel):
    """Public customer support contact details."""
    contact_id: str
    email: str
    phone: str
    whatsapp: str | None = None
    business_hours: str
    address: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ContactInfoUpdate(BaseModel):
    """Payload to update contact details (Admin)."""
    email: EmailStr | None = None
    phone: str | None = None
    whatsapp: str | None = None
    business_hours: str | None = None
    address: str | None = None


class SafetyGuideline(BaseModel):
    """Safety guideline title & description for SOS."""
    title: str
    description: str


class SOSConfigRead(BaseModel):
    """Emergency helpline numbers and safety guidelines."""
    sos_id: str
    police_helpline: str
    women_helpline: str
    ambulance_helpline: str
    kaamsetu_emergency_phone: str
    safety_guidelines: list[SafetyGuideline] = Field(default_factory=list)
    emergency_instructions: list[str] = Field(default_factory=list)
    live_location_sharing_enabled: bool = True
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SOSConfigUpdate(BaseModel):
    """Payload to update SOS configuration (Admin)."""
    police_helpline: str | None = None
    women_helpline: str | None = None
    ambulance_helpline: str | None = None
    kaamsetu_emergency_phone: str | None = None
    safety_guidelines: list[SafetyGuideline] | None = None
    emergency_instructions: list[str] | None = None
    live_location_sharing_enabled: bool | None = None


# ---------------------------------------------------------------------------
# Aggregate & Export DTOs
# ---------------------------------------------------------------------------

class SupportCategoryListRead(BaseModel):
    """List of available categories across support subsystems."""
    faq_categories: list[str]
    article_categories: list[str]
    ticket_categories: list[str]


class SupportReportExport(BaseModel):
    """Support metrics export report for React Admin."""
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    priority_breakdown: dict[str, int]
    category_breakdown: dict[str, int]
    total_feedback_submissions: int
    generated_at: datetime
