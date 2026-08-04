"""
REST API routers for Reporting, Moderation & Dispute Resolution.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
from app.auth.models import User
from app.moderation.schemas import (
    AdministrativeAction,
    CaseNoteCreate,
    DisputeCreate,
    DisputeRead,
    DisputeResolveRequest,
    DisputeStatus,
    DisputeType,
    EvidenceUploadResponse,
    ModerationEscalateRequest,
    ModerationReviewRequest,
    ReportCategory,
    ReportCreate,
    ReportRead,
    ReportStatus,
    ReportUpdate,
)
from app.moderation.service import (
    DisputeService,
    EvidenceService,
    ModerationService,
    ReportService,
    ResolutionService,
)
from app.utils.enums import UserRole

# Routers
reports_router = APIRouter(prefix="/reports", tags=["Reporting & Moderation"])
moderation_router = APIRouter(prefix="/moderation", tags=["Reporting & Moderation"])
disputes_router = APIRouter(prefix="/disputes", tags=["Dispute Resolution"])


# ===========================================================================
# 1. REPORTING ENDPOINTS
# ===========================================================================

@reports_router.post(
    "",
    response_model=ReportRead,
    summary="Submit platform report",
    description="Customer or worker files a report regarding policy violation or poor service.",
)
async def create_report(
    req: ReportCreate,
    current_user: ActiveUserDep,
) -> ReportRead:
    """Submit report."""
    report = await ReportService.create_report(str(current_user.id), req)
    return await ReportService.get_report_detail(report.report_id)


@reports_router.get(
    "",
    response_model=list[ReportRead],
    summary="Get platform reports",
    description="Retrieve reports with filtering options.",
)
async def list_reports(
    current_user: ActiveUserDep,
    report_status: ReportStatus | None = Query(default=None, alias="status"),
    category: ReportCategory | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ReportRead]:
    """List reports."""
    user_id = str(current_user.id) if current_user.role != UserRole.ADMIN else None
    reports = await ReportService.list_reports(
        user_id=user_id, status=report_status, category=category, skip=skip, limit=limit
    )
    result = []
    for r in reports:
        result.append(await ReportService.get_report_detail(r.report_id))
    return result


@reports_router.get(
    "/{id}",
    response_model=ReportRead,
    summary="Get report detail",
    description="Fetch full detail of a report including evidence files and timeline notes.",
)
async def get_report_detail(
    id: str,
    current_user: ActiveUserDep,
) -> ReportRead:
    """Get report detail."""
    return await ReportService.get_report_detail(id)


@reports_router.put(
    "/{id}",
    response_model=ReportRead,
    summary="Update report status",
    description="Update report status or resolution details.",
)
async def update_report(
    id: str,
    req: ReportUpdate,
    current_user: ActiveUserDep,
) -> ReportRead:
    """Update report."""
    actor_info = {"id": str(current_user.id), "role": current_user.role.value, "email": current_user.email}
    await ReportService.update_report(id, req, actor_info)
    return await ReportService.get_report_detail(id)


@reports_router.post(
    "/{id}/evidence",
    response_model=EvidenceUploadResponse,
    summary="Upload report evidence file",
    description="Upload evidence document or image to Cloudinary for a report.",
)
async def upload_report_evidence(
    id: str,
    current_user: ActiveUserDep,
    description: str | None = Form(default=None, description="Evidence description"),
    file: UploadFile = File(..., description="Binary file bytes"),
) -> EvidenceUploadResponse:
    """Upload report evidence."""
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty.")

    evidence = await EvidenceService.upload_evidence(
        case_id=id,
        uploader_id=str(current_user.id),
        file_bytes=file_bytes,
        filename=file.filename or f"evidence_{id[:8]}.bin",
        mime_type=file.content_type or "application/octet-stream",
        description=description,
    )
    return EvidenceUploadResponse.model_validate(evidence)


# ===========================================================================
# 2. MODERATION ENDPOINTS
# ===========================================================================

@moderation_router.post(
    "/review",
    response_model=ReportRead,
    summary="Moderator review of report",
    description="Moderator assigns severity and transitions report state to 'under_review' (Moderator/Admin).",
)
async def review_moderation_report(
    req: ModerationReviewRequest,
    admin_user: AdminUserDep,
) -> ReportRead:
    """Moderator review."""
    mod_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    await ModerationService.review_report(mod_info, req)
    return await ReportService.get_report_detail(req.report_id)


@moderation_router.post(
    "/escalate",
    summary="Escalate case to senior admin",
    description="Escalate a report or dispute case to senior administration.",
)
async def escalate_moderation_case(
    req: ModerationEscalateRequest,
    admin_user: AdminUserDep,
) -> dict[str, str]:
    """Escalate case."""
    mod_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    m_case = await ModerationService.escalate_case(mod_info, req)
    return {"message": "Case escalated successfully", "case_id": m_case.case_id}


# ===========================================================================
# 3. DISPUTE RESOLUTION ENDPOINTS
# ===========================================================================

@disputes_router.post(
    "/create",
    response_model=DisputeRead,
    summary="Create formal dispute",
    description="Customer or worker opens a formal dispute case.",
)
async def create_dispute(
    req: DisputeCreate,
    current_user: ActiveUserDep,
) -> DisputeRead:
    """Create dispute."""
    dispute = await DisputeService.create_dispute(str(current_user.id), req)
    return await DisputeService.get_dispute_detail(dispute.dispute_id)


@disputes_router.get(
    "",
    response_model=list[DisputeRead],
    summary="Get disputes",
    description="Retrieve dispute cases.",
)
async def list_disputes(
    current_user: ActiveUserDep,
    dispute_status: DisputeStatus | None = Query(default=None, alias="status"),
    dispute_type: DisputeType | None = Query(default=None, alias="type"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[DisputeRead]:
    """List disputes."""
    user_id = str(current_user.id) if current_user.role != UserRole.ADMIN else None
    disputes = await DisputeService.list_disputes(
        user_id=user_id, status=dispute_status, dispute_type=dispute_type, skip=skip, limit=limit
    )
    result = []
    for d in disputes:
        result.append(await DisputeService.get_dispute_detail(d.dispute_id))
    return result


@disputes_router.put(
    "/{id}/resolve",
    response_model=DisputeRead,
    summary="Resolve dispute & apply administrative actions",
    description="Admin resolves dispute and executes administrative actions (warnings, trust score adjustments, restrictions, suspensions, bans).",
)
async def resolve_dispute(
    id: str,
    req: DisputeResolveRequest,
    admin_user: AdminUserDep,
) -> DisputeRead:
    """Resolve dispute."""
    req.dispute_id = id
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    await ResolutionService.resolve_dispute(admin_info, req)
    return await DisputeService.get_dispute_detail(id)
