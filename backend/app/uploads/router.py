"""
Uploads router.

Endpoints (to be implemented):
    POST   /image    — Upload an image (Cloudinary)
    POST   /document — Upload a document
    DELETE /{file_id} — Delete uploaded file
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Dict, Any

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.uploads.service import CloudinaryService
from app.booking.models import Booking
from app.utils.enums import UserRole

from datetime import datetime, timezone

router = APIRouter()

@router.post("/image")
@router.post("/file")
async def upload_general_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload an image or media file to Cloudinary and return metadata.
    Enforces strict MIME type whitelisting and 10MB max file size.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WEBP, and PDF files are allowed",
        )

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 10MB limit",
        )
    url, public_id, resource_type, size = CloudinaryService.upload_booking_media(
        file_bytes=file_bytes,
        filename=file.filename or "media_upload",
        user_id=str(current_user.id),
        booking_id="inspection",
    )
    return {
        "secure_url": url,
        "url": url,
        "public_id": public_id,
        "resource_type": resource_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "size": size,
    }

@router.post("/booking-media")
async def upload_booking_media(
    booking_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Upload media (image or PDF) for an active booking.
    """
    from beanie import PydanticObjectId
    if not PydanticObjectId.is_valid(booking_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID format",
        )

    # 1. Validate booking and ownership
    booking = await Booking.get(PydanticObjectId(booking_id))
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
        
    is_customer = str(booking.customer_id) == str(current_user.id)
    is_worker = booking.worker_id is not None and str(booking.worker_id) == str(current_user.id)
    is_admin = getattr(current_user, "role", None) == UserRole.ADMIN
    if not (is_customer or is_worker or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to upload media for this booking",
        )

    # 2. Validate file size (max 5MB) and type
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the 5MB limit",
        )
        
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only JPEG, PNG, WEBP, and PDF files are allowed",
        )

    # 3. Upload to Cloudinary
    url, public_id, resource_type, size = CloudinaryService.upload_booking_media(
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        user_id=str(current_user.id),
        booking_id=booking_id,
    )

    return {
        "url": url,
        "type": "document" if resource_type == "raw" else "image",
        "name": file.filename,
        "size": size,
    }
