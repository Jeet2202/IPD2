"""
REST API endpoints for Worker Verification & Trust Management.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep, WorkerUserDep
from app.auth.models import User
from app.verification.schemas import (
    DocumentUploadResponse,
    TrustBadgeRead,
    TrustBadgeRule,
    VerificationApprovalRequest,
    VerificationRead,
    VerificationRejectionRequest,
    VerificationResubmitRequest,
    VerificationReviewRequest,
    VerificationStatusRead,
    VerificationSubmitRequest,
)
from app.verification.service import (
    ApprovalService,
    BadgeService,
    VerificationDocumentService,
    VerificationService,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. POST /verification/upload
# ---------------------------------------------------------------------------

@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload verification document",
    description="Worker uploads a verification document (PDF, PNG, JPG) to Cloudinary & MongoDB.",
)
async def upload_verification_document(
    current_worker: WorkerUserDep,
    document_type: str = Form(..., description="Document type e.g. aadhaar, pan, driving_license, address_proof, skill_certificate"),
    document_number: str | None = Form(default=None, description="Optional document ID number"),
    file: UploadFile = File(..., description="Binary document file bytes"),
) -> DocumentUploadResponse:
    """Upload verification document."""
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty.")

    doc = await VerificationDocumentService.upload_document(
        worker_id=str(current_worker.id),
        document_type=document_type,
        file_bytes=file_bytes,
        filename=file.filename or f"{document_type}.bin",
        mime_type=file.content_type or "application/octet-stream",
        document_number=document_number,
    )
    return DocumentUploadResponse.model_validate(doc)


# ---------------------------------------------------------------------------
# 2. POST /verification/submit
# ---------------------------------------------------------------------------

@router.post(
    "/submit",
    response_model=VerificationRead,
    summary="Submit verification request",
    description="Worker submits a verification request for admin review.",
)
async def submit_verification(
    req: VerificationSubmitRequest,
    current_worker: WorkerUserDep,
) -> VerificationRead:
    """Submit verification request."""
    verification = await VerificationService.submit_verification(
        worker_id=str(current_worker.id),
        req=req,
    )
    return VerificationRead.model_validate(verification)


# ---------------------------------------------------------------------------
# 3. GET /verification/status
# ---------------------------------------------------------------------------

@router.get(
    "/status",
    response_model=VerificationStatusRead,
    summary="Get verification status overview",
    description="Retrieve worker verification status across all verification categories.",
)
async def get_verification_status(
    current_user: ActiveUserDep,
    target_worker_id: str | None = Query(default=None, description="Target worker ID (Admin only)"),
) -> VerificationStatusRead:
    """Get verification status overview."""
    worker_id = str(current_user.id)
    if target_worker_id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can inspect verification status of other workers.",
            )
        worker_id = str(target_worker_id)

    return await VerificationService.get_verification_status(worker_id)


# ---------------------------------------------------------------------------
# 4. GET /verification/history
# ---------------------------------------------------------------------------

@router.get(
    "/history",
    response_model=list[VerificationRead],
    summary="Get verification submission history",
    description="Retrieve history of worker verification requests.",
)
async def get_verification_history(
    current_user: ActiveUserDep,
    target_worker_id: str | None = Query(default=None, description="Target worker ID (Admin only)"),
) -> list[VerificationRead]:
    """Get verification submission history."""
    worker_id = str(current_user.id)
    if target_worker_id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can access verification history of other workers.",
            )
        worker_id = str(target_worker_id)

    records = await VerificationService.get_verification_history(worker_id)
    return [VerificationRead.model_validate(r) for r in records]


# ---------------------------------------------------------------------------
# 5. PUT /verification/resubmit
# ---------------------------------------------------------------------------

@router.put(
    "/resubmit",
    response_model=VerificationRead,
    summary="Resubmit requested verification",
    description="Worker resubmits updated verification or documents.",
)
async def resubmit_verification(
    req: VerificationResubmitRequest,
    current_worker: WorkerUserDep,
) -> VerificationRead:
    """Resubmit requested verification."""
    updated = await VerificationService.resubmit_verification(
        worker_id=str(current_worker.id),
        verification_id=req.verification_id,
        new_document_ids=req.new_document_ids,
        notes=req.notes,
    )
    return VerificationRead.model_validate(updated)


# ---------------------------------------------------------------------------
# 6. POST /verification/review
# ---------------------------------------------------------------------------

@router.post(
    "/review",
    response_model=VerificationRead,
    summary="Start admin review",
    description="Admin transitions a verification request to 'under_review' (Admin restricted).",
)
async def start_verification_review(
    req: VerificationReviewRequest,
    admin_user: AdminUserDep,
) -> VerificationRead:
    """Start admin review."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    updated = await ApprovalService.start_review(
        admin_user=admin_info,
        verification_id=req.verification_id,
        review_notes=req.review_notes,
    )
    return VerificationRead.model_validate(updated)


# ---------------------------------------------------------------------------
# 7. POST /verification/approve
# ---------------------------------------------------------------------------

@router.post(
    "/approve",
    response_model=VerificationRead,
    summary="Approve verification request",
    description="Admin approves verification request, updates Trust Score, and grants trust badges (Admin restricted).",
)
async def approve_verification(
    req: VerificationApprovalRequest,
    admin_user: AdminUserDep,
) -> VerificationRead:
    """Approve verification request."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    approved = await ApprovalService.approve_verification(
        admin_user=admin_info,
        verification_id=req.verification_id,
        review_notes=req.review_notes,
        grant_badges=req.grant_badges,
    )
    return VerificationRead.model_validate(approved)


# ---------------------------------------------------------------------------
# 8. POST /verification/reject
# ---------------------------------------------------------------------------

@router.post(
    "/reject",
    response_model=VerificationRead,
    summary="Reject or request resubmission",
    description="Admin rejects verification or demands document resubmission (Admin restricted).",
)
async def reject_verification(
    req: VerificationRejectionRequest,
    admin_user: AdminUserDep,
) -> VerificationRead:
    """Reject or request resubmission."""
    admin_info = {"id": str(admin_user.id), "role": admin_user.role.value, "email": admin_user.email}
    rejected = await ApprovalService.reject_verification(
        admin_user=admin_info,
        verification_id=req.verification_id,
        review_notes=req.review_notes,
        request_resubmission=req.request_resubmission,
    )
    return VerificationRead.model_validate(rejected)


# ---------------------------------------------------------------------------
# 9. GET /verification/badges
# ---------------------------------------------------------------------------

@router.get(
    "/badges",
    response_model=list[TrustBadgeRead],
    summary="Get worker earned badges",
    description="Retrieve list of active trust badges granted to a worker.",
)
async def get_worker_badges(
    current_user: ActiveUserDep,
    target_worker_id: str | None = Query(default=None, description="Target worker ID"),
) -> list[TrustBadgeRead]:
    """Get worker earned badges."""
    worker_id = str(current_user.id)
    if target_worker_id:
        worker_id = str(target_worker_id)

    badges = await BadgeService.get_worker_badges(worker_id)
    return [TrustBadgeRead.model_validate(b) for b in badges]
