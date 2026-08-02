"""
Customer Profile API Router — Profile management and photo upload endpoints for customers.
"""

import logging

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.auth.repository import AuthRepository
from app.core.dependencies import CustomerDep
from app.core.exceptions import NotFoundException
from app.customer.schemas import CustomerProfileResponse, UpdateCustomerProfileRequest
from app.customer.service import CustomerService

logger = logging.getLogger(__name__)

router = APIRouter()


async def _get_customer_user(current_user: CustomerDep):
    """Retrieve full User Beanie document for current customer."""
    user = await AuthRepository.find_user_by_id(current_user.id)
    if not user:
        raise NotFoundException(message="Customer user profile not found", error_code="USER_NOT_FOUND")
    return user


@router.get(
    "/profile",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get customer profile",
    description="Retrieve the full profile of the currently authenticated customer, including completion status.",
)
@router.get("/me", response_model=CustomerProfileResponse, include_in_schema=False)
async def get_customer_profile(
    user=Depends(_get_customer_user),
) -> CustomerProfileResponse:
    """Get current authenticated customer's profile."""
    return await CustomerService.get_customer_profile(user)


@router.put(
    "/profile",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update customer profile",
    description="Update profile details (DOB, gender, language, addresses, notification preferences) and display name.",
)
@router.put("/me", response_model=CustomerProfileResponse, include_in_schema=False)
async def update_customer_profile(
    payload: UpdateCustomerProfileRequest,
    user=Depends(_get_customer_user),
) -> CustomerProfileResponse:
    """Update current authenticated customer's profile."""
    return await CustomerService.update_customer_profile(user, payload)


@router.post(
    "/profile/photo",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload or replace customer profile photo",
    description="Upload multipart image file (jpg, jpeg, png, webp, max 2MB) to Cloudinary and update customer profile.",
)
@router.post("/photo", response_model=CustomerProfileResponse, include_in_schema=False)
async def upload_customer_profile_photo(
    file: UploadFile = File(..., description="Image file binary multipart upload"),
    user=Depends(_get_customer_user),
) -> CustomerProfileResponse:
    """Upload or replace profile photo for customer."""
    return await CustomerService.upload_profile_photo(user, file)


@router.delete(
    "/profile/photo",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete customer profile photo",
    description="Remove customer profile photo from Cloudinary storage and database.",
)
@router.delete("/photo", response_model=CustomerProfileResponse, include_in_schema=False)
async def delete_customer_profile_photo(
    user=Depends(_get_customer_user),
) -> CustomerProfileResponse:
    """Delete profile photo for customer."""
    return await CustomerService.delete_profile_photo(user)
