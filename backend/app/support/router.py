"""
REST API endpoints for Help Center & Customer Support module.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
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
    TicketCreate,
    TicketPriority,
    TicketRead,
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

router = APIRouter()


# =============================================================================
# 1. Flutter Customer & Worker User Endpoints
# =============================================================================

# --- FAQs ---

@router.get(
    "/help/faqs",
    response_model=list[FAQRead],
    summary="Get FAQs",
    description="Retrieve Frequently Asked Questions with optional category, popular filter, or search query.",
)
async def list_faqs(
    category: str | None = Query(default=None, description="Filter by category"),
    popular: bool = Query(default=False, description="Filter popular FAQs"),
    search: str | None = Query(default=None, description="Search query string"),
) -> list[FAQRead]:
    """Get FAQs."""
    return await FAQService.list_faqs(category=category, popular_only=popular, search_query=search)


@router.get(
    "/help/faqs/{faq_id}",
    response_model=FAQRead,
    summary="Get FAQ details",
    description="Retrieve detailed FAQ answer and increment view counter.",
)
async def get_faq(
    faq_id: str,
    current_user: ActiveUserDep,
) -> FAQRead:
    """Get FAQ details."""
    return await FAQService.get_faq_by_id(faq_id=faq_id, user_id=str(current_user.id))


# --- Knowledge Base Articles ---

@router.get(
    "/help/articles",
    response_model=list[HelpArticleRead],
    summary="Get Help Articles",
    description="Retrieve Knowledge Base help articles and troubleshooting guides.",
)
async def list_articles(
    category: str | None = Query(default=None, description="Filter by article category"),
    role: str | None = Query(default=None, description="Target role filter (customer, worker, all)"),
    search: str | None = Query(default=None, description="Search query string"),
) -> list[HelpArticleRead]:
    """Get Help Articles."""
    return await KnowledgeBaseService.list_articles(category=category, role=role, search_query=search)


@router.get(
    "/help/articles/{article_id}",
    response_model=HelpArticleRead,
    summary="Get Help Article details",
    description="Retrieve Help Article details and increment view counter.",
)
async def get_article(
    article_id: str,
    current_user: ActiveUserDep,
) -> HelpArticleRead:
    """Get Help Article details."""
    return await KnowledgeBaseService.get_article_by_id(article_id=article_id, user_id=str(current_user.id))


@router.get(
    "/help/categories",
    response_model=SupportCategoryListRead,
    summary="Get support categories",
    description="Retrieve available categories for FAQs, Knowledge Base articles, and Support Tickets.",
)
async def get_support_categories() -> SupportCategoryListRead:
    """Get support categories."""
    return await TicketManagementService.get_support_categories()


# --- Support Tickets ---

@router.post(
    "/support/tickets",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create support ticket",
    description="Submit a new support ticket with subject, description, priority, and optional Cloudinary attachments.",
)
async def create_ticket(
    current_user: ActiveUserDep,
    req: TicketCreate,
) -> TicketRead:
    """Create support ticket."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return await SupportTicketService.create_ticket(
        user_id=str(current_user.id), user_role=user_role, req=req
    )


@router.get(
    "/support/tickets",
    response_model=list[TicketRead],
    summary="Get user support tickets",
    description="Retrieve list of support tickets submitted by current user.",
)
async def list_user_tickets(
    current_user: ActiveUserDep,
    ticket_status: TicketStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[TicketRead]:
    """Get user support tickets."""
    return await SupportTicketService.list_user_tickets(
        user_id=str(current_user.id), status=ticket_status, skip=skip, limit=limit
    )


@router.get(
    "/support/tickets/{ticket_id}",
    response_model=TicketRead,
    summary="Get support ticket details",
    description="Retrieve support ticket details and full response message thread.",
)
async def get_user_ticket(
    current_user: ActiveUserDep,
    ticket_id: str,
) -> TicketRead:
    """Get support ticket details."""
    return await SupportTicketService.get_user_ticket_by_id(
        user_id=str(current_user.id), ticket_id=ticket_id
    )


@router.put(
    "/support/tickets/{ticket_id}",
    response_model=TicketRead,
    summary="Update or reply to support ticket",
    description="Post a message response or update status (e.g. close or reopen ticket).",
)
async def update_user_ticket(
    current_user: ActiveUserDep,
    ticket_id: str,
    reply: TicketReplyRequest | None = None,
    status_update: TicketStatusUpdateRequest | None = None,
) -> TicketRead:
    """Update or reply to support ticket."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)

    if reply:
        return await SupportTicketService.reply_to_ticket(
            user_id=str(current_user.id), user_role=user_role, ticket_id=ticket_id, req=reply
        )
    if status_update:
        return await SupportTicketService.update_ticket_status(
            user_id=str(current_user.id), user_role=user_role, ticket_id=ticket_id, req=status_update
        )

    raise HTTPException(status_code=400, detail="Must provide either a reply message or a status update.")


# --- Feedback, Contact & SOS ---

@router.post(
    "/support/feedback",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit app feedback",
    description="Submit app feedback, bug reports, feature requests, or general suggestions.",
)
async def submit_feedback(
    current_user: ActiveUserDep,
    req: FeedbackCreate,
) -> FeedbackRead:
    """Submit app feedback."""
    user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return await FeedbackService.submit_feedback(
        user_id=str(current_user.id), user_role=user_role, req=req
    )


@router.get(
    "/support/contact",
    response_model=ContactInfoRead,
    summary="Get support contact information",
    description="Retrieve support email, helpline phone number, WhatsApp link, and business operating hours.",
)
async def get_contact_info() -> ContactInfoRead:
    """Get support contact information."""
    return await SupportContactService.get_contact_info()


@router.get(
    "/support/sos",
    response_model=SOSConfigRead,
    summary="Get SOS emergency configuration",
    description="Retrieve emergency helpline numbers (police, women helpline, ambulance), safety guidelines, and instructions.",
)
async def get_sos_config(
    current_user: ActiveUserDep,
) -> SOSConfigRead:
    """Get SOS emergency configuration."""
    return await SOSService.get_sos_config(user_id=str(current_user.id))


# =============================================================================
# 2. React Admin Management Endpoints
# =============================================================================

# --- FAQ Admin Management ---

@router.post(
    "/admin/support/faqs",
    response_model=FAQRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create FAQ (Admin)",
    description="Create a new FAQ entry in the catalog.",
)
async def admin_create_faq(
    admin: AdminUserDep,
    req: FAQCreate,
) -> FAQRead:
    """Create FAQ (Admin)."""
    return await FAQService.create_faq(req)


@router.put(
    "/admin/support/faqs/{faq_id}",
    response_model=FAQRead,
    summary="Update FAQ (Admin)",
    description="Update an existing FAQ entry.",
)
async def admin_update_faq(
    admin: AdminUserDep,
    faq_id: str,
    req: FAQUpdate,
) -> FAQRead:
    """Update FAQ (Admin)."""
    return await FAQService.update_faq(faq_id, req)


@router.delete(
    "/admin/support/faqs/{faq_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete FAQ (Admin)",
    description="Delete an FAQ entry from the catalog.",
)
async def admin_delete_faq(
    admin: AdminUserDep,
    faq_id: str,
) -> dict[str, str]:
    """Delete FAQ (Admin)."""
    await FAQService.delete_faq(faq_id)
    return {"message": f"FAQ '{faq_id}' deleted successfully."}


# --- Knowledge Base Admin Management ---

@router.post(
    "/admin/support/articles",
    response_model=HelpArticleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Help Article (Admin)",
    description="Create a new Knowledge Base help article.",
)
async def admin_create_article(
    admin: AdminUserDep,
    req: HelpArticleCreate,
) -> HelpArticleRead:
    """Create Help Article (Admin)."""
    return await KnowledgeBaseService.create_article(req)


@router.put(
    "/admin/support/articles/{article_id}",
    response_model=HelpArticleRead,
    summary="Update Help Article (Admin)",
    description="Update an existing Knowledge Base help article.",
)
async def admin_update_article(
    admin: AdminUserDep,
    article_id: str,
    req: HelpArticleUpdate,
) -> HelpArticleRead:
    """Update Help Article (Admin)."""
    return await KnowledgeBaseService.update_article(article_id, req)


@router.delete(
    "/admin/support/articles/{article_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Help Article (Admin)",
    description="Delete a Knowledge Base help article.",
)
async def admin_delete_article(
    admin: AdminUserDep,
    article_id: str,
) -> dict[str, str]:
    """Delete Help Article (Admin)."""
    await KnowledgeBaseService.delete_article(article_id)
    return {"message": f"Help Article '{article_id}' deleted successfully."}


# --- Support Tickets Admin Management ---

@router.get(
    "/admin/support/tickets",
    response_model=list[TicketRead],
    summary="List all support tickets (Admin)",
    description="List support tickets across all users with status, priority, and category filters.",
)
async def admin_list_tickets(
    admin: AdminUserDep,
    ticket_status: TicketStatus | None = Query(default=None, alias="status"),
    priority: TicketPriority | None = Query(default=None),
    category: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[TicketRead]:
    """List all support tickets (Admin)."""
    return await TicketManagementService.list_all_tickets(
        status=ticket_status, priority=priority, category=category, skip=skip, limit=limit
    )


@router.put(
    "/admin/support/tickets/{ticket_id}/reply",
    response_model=TicketRead,
    summary="Reply to support ticket (Admin)",
    description="Post an administrative response on a support ticket thread.",
)
async def admin_reply_ticket(
    admin: AdminUserDep,
    ticket_id: str,
    req: TicketReplyRequest,
) -> TicketRead:
    """Reply to support ticket (Admin)."""
    return await SupportTicketService.reply_to_ticket(
        user_id=str(admin.id), user_role="admin", ticket_id=ticket_id, req=req
    )


@router.put(
    "/admin/support/tickets/{ticket_id}/status",
    response_model=TicketRead,
    summary="Update ticket status & priority (Admin)",
    description="Update ticket status, priority, or assign an administrator.",
)
async def admin_update_ticket_status(
    admin: AdminUserDep,
    ticket_id: str,
    req: TicketStatusUpdateRequest,
) -> TicketRead:
    """Update ticket status & priority (Admin)."""
    return await SupportTicketService.update_ticket_status(
        user_id=str(admin.id), user_role="admin", ticket_id=ticket_id, req=req
    )


# --- Contact & SOS Configuration Admin Management ---

@router.put(
    "/admin/support/contact",
    response_model=ContactInfoRead,
    summary="Configure support contact information (Admin)",
    description="Update public email, phone, business hours, and address.",
)
async def admin_update_contact_info(
    admin: AdminUserDep,
    req: ContactInfoUpdate,
) -> ContactInfoRead:
    """Configure support contact information (Admin)."""
    return await SupportContactService.update_contact_info(req)


@router.put(
    "/admin/support/sos",
    response_model=SOSConfigRead,
    summary="Configure SOS emergency helplines & safety guidelines (Admin)",
    description="Update police/women/ambulance helpline numbers and safety guidelines.",
)
async def admin_update_sos_config(
    admin: AdminUserDep,
    req: SOSConfigUpdate,
) -> SOSConfigRead:
    """Configure SOS emergency helplines & safety guidelines (Admin)."""
    return await SOSService.update_sos_config(req)


@router.get(
    "/admin/support/feedback",
    response_model=list[FeedbackRead],
    summary="View feedback submissions (Admin)",
    description="Retrieve user app feedback, bug reports, and feature requests.",
)
async def admin_list_feedback(
    admin: AdminUserDep,
    category: str | None = Query(default=None),
    feedback_status: str | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[FeedbackRead]:
    """View feedback submissions (Admin)."""
    return await FeedbackService.list_feedback(
        category=category, status=feedback_status, skip=skip, limit=limit
    )


@router.get(
    "/admin/support/reports/export",
    response_model=SupportReportExport,
    summary="Export support metrics report (Admin)",
    description="Retrieve aggregate support metrics report for React Admin dashboard.",
)
async def admin_export_support_report(
    admin: AdminUserDep,
) -> SupportReportExport:
    """Export support metrics report (Admin)."""
    return await TicketManagementService.export_support_report()
