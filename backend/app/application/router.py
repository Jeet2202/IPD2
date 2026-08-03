"""
JobApplication FastAPI Router — worker application management endpoints.

Endpoints:
    POST /api/v1/worker/applications             Apply for an open marketplace booking.
    GET /api/v1/worker/applications              List worker's submitted applications.
    GET /api/v1/worker/applications/{applicationId} Get details of a worker's application.
"""

from fastapi import APIRouter, Depends, Query, status

from app.application.schemas import (
    JobApplicationCreateRequest,
    JobApplicationPaginatedResponse,
    JobApplicationResponse,
)
from app.application.service import JobApplicationService
from app.auth.dependencies import WorkerUserDep
from app.auth.models import User
from app.utils.enums import ApplicationStatus

router = APIRouter()


def get_job_application_service() -> JobApplicationService:
    return JobApplicationService()


@router.post(
    "",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply for a marketplace booking",
    description=(
        "Submits a worker expression of interest for an open marketplace booking. "
        "Does NOT assign the worker or alter booking status from PENDING. "
        "Prevented if booking is closed/assigned or if worker already applied."
    ),
)
@router.post(
    "/",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_job_application(
    payload: JobApplicationCreateRequest,
    worker: WorkerUserDep,
    service: JobApplicationService = Depends(get_job_application_service),
) -> JobApplicationResponse:
    return await service.apply_for_job(worker, payload)


@router.get(
    "",
    response_model=JobApplicationPaginatedResponse,
    summary="List worker job applications",
    description="Returns a paginated list of job applications submitted by the authenticated worker.",
)
@router.get(
    "/",
    response_model=JobApplicationPaginatedResponse,
    include_in_schema=False,
)
async def list_worker_job_applications(
    worker: WorkerUserDep,
    status: ApplicationStatus | None = Query(default=None, description="Filter by application status"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    service: JobApplicationService = Depends(get_job_application_service),
) -> JobApplicationPaginatedResponse:
    return await service.list_worker_applications(
        worker, status=status, page=page, page_size=page_size
    )


@router.get(
    "/{application_id}",
    response_model=JobApplicationResponse,
    summary="Get job application details",
    description="Returns details of a specific job application. Workers can only view their own applications.",
)
async def get_worker_job_application_detail(
    application_id: str,
    worker: WorkerUserDep,
    service: JobApplicationService = Depends(get_job_application_service),
) -> JobApplicationResponse:
    return await service.get_worker_application_detail(worker, application_id)
