"""
REST API endpoints for Privacy, Compliance & Data Protection.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth.dependencies import ActiveUserDep, AdminUserDep
from app.auth.models import User
from app.privacy.schemas import (
    AccountDeletionRequest,
    ConsentRead,
    ConsentUpdateRequest,
    DataExportRead,
    DataExportRequest,
    PrivacyProfileRead,
    PrivacyRequestRead,
    RetentionPolicyRead,
)
from app.privacy.service import (
    ConsentService,
    DataAccessService,
    DataExportService,
    DataRetentionService,
    PrivacyService,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# 1. GET /privacy/profile
# ---------------------------------------------------------------------------

@router.get(
    "/profile",
    response_model=PrivacyProfileRead,
    summary="Get user privacy profile",
    description="Retrieve personal data overview, deletion request status, and consent preferences.",
)
async def get_privacy_profile(
    current_user: ActiveUserDep,
) -> PrivacyProfileRead:
    """Get privacy profile."""
    return await DataAccessService.get_user_privacy_profile(str(current_user.id))


# ---------------------------------------------------------------------------
# 2. GET /privacy/consents
# ---------------------------------------------------------------------------

@router.get(
    "/consents",
    response_model=list[ConsentRead],
    summary="Get user consent preferences",
    description="Retrieve list of active user privacy consents and policy acceptance versions.",
)
async def get_user_consents(
    current_user: ActiveUserDep,
) -> list[ConsentRead]:
    """Get consents."""
    consents = await ConsentService.get_user_consents(str(current_user.id))
    return [ConsentRead.model_validate(c) for c in consents]


# ---------------------------------------------------------------------------
# 3. PUT /privacy/consents
# ---------------------------------------------------------------------------

@router.put(
    "/consents",
    response_model=list[ConsentRead],
    summary="Update consent preferences",
    description="Update user privacy consent settings and audit compliance history.",
)
async def update_user_consents(
    req: ConsentUpdateRequest,
    request: Request,
    current_user: ActiveUserDep,
) -> list[ConsentRead]:
    """Update consents."""
    ip_addr = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    updated = await ConsentService.update_user_consents(
        user_id=str(current_user.id),
        req=req,
        ip_address=ip_addr,
        user_agent=user_agent,
    )
    return [ConsentRead.model_validate(c) for c in updated]


# ---------------------------------------------------------------------------
# 4. POST /privacy/export
# ---------------------------------------------------------------------------

@router.post(
    "/export",
    response_model=DataExportRead,
    summary="Request personal data export",
    description="Generate downloadable personal data export in JSON or CSV format.",
)
async def request_data_export(
    req: DataExportRequest,
    current_user: ActiveUserDep,
) -> DataExportRead:
    """Request data export."""
    return await DataExportService.generate_data_export(
        user_id=str(current_user.id),
        format_type=req.format,
    )


# ---------------------------------------------------------------------------
# 5. POST /privacy/delete-request
# ---------------------------------------------------------------------------

@router.post(
    "/delete-request",
    response_model=PrivacyRequestRead,
    summary="Request account deletion",
    description="Submit an account deletion request with a 30-day grace period.",
)
async def request_account_deletion(
    req: AccountDeletionRequest,
    current_user: ActiveUserDep,
) -> PrivacyRequestRead:
    """Request account deletion."""
    request_doc = await PrivacyService.request_account_deletion(
        user_id=str(current_user.id),
        reason=req.reason,
    )
    return PrivacyRequestRead.model_validate(request_doc)


# ---------------------------------------------------------------------------
# 6. DELETE /privacy/delete-request
# ---------------------------------------------------------------------------

@router.delete(
    "/delete-request",
    response_model=PrivacyRequestRead,
    summary="Cancel account deletion request",
    description="Cancel a pending account deletion request during the 30-day grace period.",
)
async def cancel_account_deletion(
    current_user: ActiveUserDep,
) -> PrivacyRequestRead:
    """Cancel account deletion."""
    cancelled = await PrivacyService.cancel_account_deletion(str(current_user.id))
    return PrivacyRequestRead.model_validate(cancelled)


# ---------------------------------------------------------------------------
# 7. GET /privacy/requests
# ---------------------------------------------------------------------------

@router.get(
    "/requests",
    response_model=list[PrivacyRequestRead],
    summary="Get user privacy requests",
    description="Retrieve history of privacy and account deletion requests.",
)
async def get_privacy_requests(
    current_user: ActiveUserDep,
) -> list[PrivacyRequestRead]:
    """Get privacy requests."""
    requests_list = await PrivacyService.get_user_privacy_requests(str(current_user.id))
    return [PrivacyRequestRead.model_validate(r) for r in requests_list]


# ---------------------------------------------------------------------------
# 8. GET /privacy/policies
# ---------------------------------------------------------------------------

@router.get(
    "/policies",
    response_model=list[RetentionPolicyRead],
    summary="Get data retention policies",
    description="Retrieve active platform data retention rules.",
)
async def get_retention_policies(
    current_user: ActiveUserDep,
) -> list[RetentionPolicyRead]:
    """Get retention policies."""
    policies = await DataRetentionService.list_retention_policies()
    return [RetentionPolicyRead.model_validate(p) for p in policies]
