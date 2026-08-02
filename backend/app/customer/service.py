"""
Customer Profile Service — Business logic for customer profile management, photo upload, & completion tracking.
"""

import logging
from fastapi import UploadFile

from app.auth.models import User
from app.customer.models import CustomerProfile, NotificationPreferences
from app.customer.repository import CustomerRepository
from app.customer.schemas import (
    CustomerProfileResponse,
    NotificationPreferencesSchema,
    UpdateCustomerProfileRequest,
)
from app.uploads.service import CloudinaryService
from app.uploads.validation import validate_profile_image

logger = logging.getLogger(__name__)


class CustomerService:
    """Business logic handler for customer profile endpoints."""

    @staticmethod
    def calculate_completion_percentage(user: User, profile: CustomerProfile) -> tuple[int, bool]:
        """
        Calculate profile completion percentage (0-100%) and boolean threshold (>= 70%).

        Scoring Rules:
            - Basic User Credentials (full_name, email, phone): 40%
            - Preferred Language configured: 10%
            - Gender specified: 10%
            - Date of Birth specified: 10%
            - Saved Addresses (at least 1 address): 20%
            - Profile Photo uploaded: 10%
        """
        score = 0

        # Base identity (email, phone, full_name exist)
        if user.full_name and user.email and user.phone:
            score += 40

        # Preferred language
        if profile.preferred_language and profile.preferred_language.strip():
            score += 10

        # Gender
        if profile.gender is not None:
            score += 10

        # Date of birth
        if profile.date_of_birth is not None:
            score += 10

        # Saved addresses
        if profile.addresses and len(profile.addresses) > 0:
            score += 20

        # Profile photo
        if profile.profile_photo_url and profile.profile_photo_url.strip():
            score += 10

        score = min(score, 100)
        is_completed = score >= 70
        return score, is_completed

    @classmethod
    async def get_or_create_profile(cls, user: User) -> CustomerProfile:
        """Fetch customer profile for user, creating one if missing."""
        profile = await CustomerRepository.get_by_user_id(user.id)
        if not profile:
            profile = await CustomerRepository.create_profile(user.id)
        return profile

    @classmethod
    def _build_response_dto(
        cls, user: User, profile: CustomerProfile, completion_pct: int, is_completed: bool
    ) -> CustomerProfileResponse:
        """Construct standard CustomerProfileResponse DTO."""
        return CustomerProfileResponse(
            id=str(profile.id),
            user_id=str(user.id),
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            role=user.role.value,
            profile_photo_url=profile.profile_photo_url,
            profile_photo_public_id=profile.profile_photo_public_id,
            alternate_phone=profile.alternate_phone,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            preferred_language=profile.preferred_language,
            notification_preferences=NotificationPreferencesSchema(
                push=profile.notification_preferences.push,
                email=profile.notification_preferences.email,
                sms=profile.notification_preferences.sms,
            ),
            addresses=profile.addresses,
            profile_completion_percentage=completion_pct,
            profile_completed=is_completed,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @classmethod
    async def get_customer_profile(cls, user: User) -> CustomerProfileResponse:
        """Retrieve full customer profile DTO for authenticated user."""
        profile = await cls.get_or_create_profile(user)
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)

        # Sync profile_completed flag if state changed
        if profile.profile_completed != is_completed:
            profile.profile_completed = is_completed
            await CustomerRepository.save_profile(profile)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def update_customer_profile(
        cls, user: User, payload: UpdateCustomerProfileRequest
    ) -> CustomerProfileResponse:
        """Update customer profile fields and optional user full_name."""
        profile = await cls.get_or_create_profile(user)

        # 1. Update User level fields if provided
        if payload.full_name is not None and payload.full_name.strip() != user.full_name:
            user.full_name = payload.full_name.strip()
            await user.save()

        # 2. Update CustomerProfile level fields
        if payload.alternate_phone is not None:
            profile.alternate_phone = payload.alternate_phone
        if payload.date_of_birth is not None:
            profile.date_of_birth = payload.date_of_birth
        if payload.gender is not None:
            profile.gender = payload.gender
        if payload.preferred_language is not None:
            profile.preferred_language = payload.preferred_language
        if payload.notification_preferences is not None:
            profile.notification_preferences = NotificationPreferences(
                push=payload.notification_preferences.push,
                email=payload.notification_preferences.email,
                sms=payload.notification_preferences.sms,
            )
        if payload.addresses is not None:
            profile.addresses = payload.addresses

        # 3. Calculate new completion percentage
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        # 4. Save profile
        await CustomerRepository.save_profile(profile)
        logger.info("Updated customer profile for user_id=%s (completion=%d%%)", user.id, completion_pct)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def upload_profile_photo(cls, user: User, file: UploadFile) -> CustomerProfileResponse:
        """Validate, upload (or replace) customer profile photo in Cloudinary and update database."""
        profile = await cls.get_or_create_profile(user)

        # Read file bytes
        file_bytes = await file.read()

        # Validate format, extension, size, and magic bytes
        validate_profile_image(file.filename, file.content_type, file_bytes)

        # Upload / Replace in Cloudinary
        secure_url, public_id = CloudinaryService.replace_profile_image(
            file_bytes=file_bytes,
            filename=file.filename or "profile.jpg",
            user_id=str(user.id),
            old_public_id=profile.profile_photo_public_id,
        )

        # Update database fields
        profile.profile_photo_url = secure_url
        profile.profile_photo_public_id = public_id

        # Recalculate completion percentage
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        await CustomerRepository.save_profile(profile)
        logger.info("Uploaded profile photo for customer user_id=%s (url=%s)", user.id, secure_url)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def delete_profile_photo(cls, user: User) -> CustomerProfileResponse:
        """Delete customer profile photo from Cloudinary and clear database reference."""
        profile = await cls.get_or_create_profile(user)

        if profile.profile_photo_public_id:
            CloudinaryService.delete_image(profile.profile_photo_public_id)

        profile.profile_photo_url = None
        profile.profile_photo_public_id = None

        # Recalculate completion percentage
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        await CustomerRepository.save_profile(profile)
        logger.info("Deleted profile photo for customer user_id=%s", user.id)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)
