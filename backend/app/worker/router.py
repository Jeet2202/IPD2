"""
Worker Profile API Router — Profile management and photo upload endpoints for service workers.
"""

import logging

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.auth.repository import AuthRepository
from app.core.dependencies import WorkerDep
from app.core.exceptions import NotFoundException
from app.worker.dashboard_schemas import WorkerDashboardResponse
from app.worker.schemas import UpdateWorkerLocationRequest, UpdateWorkerProfileRequest, WorkerProfileResponse
from app.worker.service import WorkerService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_worker_user(current_user: WorkerDep):
    """Retrieve full User Beanie document for current worker."""
    user = await AuthRepository.find_user_by_id(current_user.id)
    if not user:
        raise NotFoundException(message="Worker user profile not found", error_code="USER_NOT_FOUND")
    return user


@router.get(
    "/dashboard",
    response_model=WorkerDashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get worker dashboard data",
    description="Retrieve aggregated payload for worker dashboard landing page.",
)
async def get_worker_dashboard(
    user=Depends(_get_worker_user),
) -> WorkerDashboardResponse:
    """Get current authenticated worker's aggregated dashboard payload."""
    return await WorkerService.get_worker_dashboard_data(user)


@router.get(
    "/profile",
    response_model=WorkerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get worker profile",
    description="Retrieve full worker profile details including skills, availability, and completion status.",
)
@router.get("/me", response_model=WorkerProfileResponse, include_in_schema=False)
async def get_worker_profile(
    user=Depends(_get_worker_user),
) -> WorkerProfileResponse:
    """Get current authenticated worker's profile."""
    return await WorkerService.get_worker_profile(user)


@router.put(
    "/profile",
    response_model=WorkerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update worker profile",
    description="Update worker bio, experience, skills, languages, hourly rate, working radius, and availability.",
)
@router.put("/me", response_model=WorkerProfileResponse, include_in_schema=False)
async def update_worker_profile(
    payload: UpdateWorkerProfileRequest,
    user=Depends(_get_worker_user),
) -> WorkerProfileResponse:
    """Update current authenticated worker's profile."""
    return await WorkerService.update_worker_profile(user, payload)


@router.post(
    "/profile/photo",
    response_model=WorkerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload or replace worker profile photo",
    description="Upload multipart image file (jpg, jpeg, png, webp, max 2MB) to Cloudinary and update worker profile.",
)
@router.post("/photo", response_model=WorkerProfileResponse, include_in_schema=False)
async def upload_worker_profile_photo(
    file: UploadFile = File(..., description="Image file binary multipart upload"),
    user=Depends(_get_worker_user),
) -> WorkerProfileResponse:
    """Upload or replace profile photo for worker."""
    return await WorkerService.upload_profile_photo(user, file)


@router.delete(
    "/profile/photo",
    response_model=WorkerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete worker profile photo",
    description="Remove worker profile photo from Cloudinary storage and database.",
)
@router.delete("/photo", response_model=WorkerProfileResponse, include_in_schema=False)
async def delete_worker_profile_photo(
    user=Depends(_get_worker_user),
) -> WorkerProfileResponse:
    """Delete profile photo for worker."""
    return await WorkerService.delete_profile_photo(user)


@router.patch(
    "/profile/location",
    response_model=WorkerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update worker current location",
    description="Update worker's real-time GPS location. Used by the app to enable geo-proximity job matching.",
)
async def update_worker_location(
    payload: UpdateWorkerLocationRequest,
    user=Depends(_get_worker_user),
) -> WorkerProfileResponse:
    """Update current GPS location for worker."""
    return await WorkerService.update_worker_location(user, payload)
