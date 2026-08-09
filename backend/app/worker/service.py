"""
Worker Profile Service — Business logic for worker profile management, photo upload, & completion tracking.
"""

import logging
from datetime import datetime, timezone
from fastapi import UploadFile

from app.auth.models import User
from app.uploads.service import CloudinaryService
from app.uploads.validation import validate_profile_image
from app.worker.models import WorkerProfile
from app.worker.repository import WorkerRepository
from app.address.models import GeoJSONPoint
from app.category.repository import CategoryRepository
from app.core.config import settings
from app.core.exceptions import BadRequestException
from app.worker.schemas import UpdateWorkerLocationRequest, UpdateWorkerProfileRequest, WorkerProfileResponse

logger = logging.getLogger(__name__)


class WorkerService:
    """Business logic handler for worker profile endpoints."""

    @classmethod
    async def get_valid_skills(cls) -> dict[str, list[str]]:
        """Return active canonical category slugs from MongoDB."""
        slugs = await CategoryRepository.get_active_category_slugs()
        return {"skills": slugs}

    @classmethod
    async def validate_and_normalize_skills(cls, skills: list[str]) -> list[str]:
        """
        Normalize and validate worker skills against active database category slugs.

        Normalization rules:
            - Trim whitespace
            - Lowercase
            - Deduplicate while preserving order
            - Reject empty values
            - Validate against canonical active category slugs in MongoDB when SKILL_VALIDATION_ENABLED is True
        """
        cleaned = []
        for item in skills:
            if not isinstance(item, str):
                continue
            normalized = item.strip().lower()
            if normalized and normalized not in cleaned:
                cleaned.append(normalized)

        valid_slugs = await CategoryRepository.get_active_category_slugs()
        if valid_slugs:
            invalid_skills = [s for s in cleaned if s not in valid_slugs]
            if invalid_skills:
                if settings.SKILL_VALIDATION_ENABLED:
                    raise BadRequestException(
                        message=f"Invalid skill domain(s): {', '.join(invalid_skills)}. Valid options: {', '.join(valid_slugs)}",
                        error_code="INVALID_SKILL",
                    )
                else:
                    logger.warning("SKILL_VALIDATION_ENABLED=False: Allowing informal worker skill(s): %s", invalid_skills)

        return cleaned

    @staticmethod
    def calculate_completion_percentage(user: User, profile: WorkerProfile) -> tuple[int, bool]:
        """
        Calculate profile completion percentage (0-100%) and boolean threshold (>= 70%).

        Scoring Rules:
            - Basic User Credentials (full_name, email, phone): 30%
            - Professional Bio (>= 20 characters): 15%
            - Registered Skills (at least 1 skill): 20%
            - Experience (> 0 years): 10%
            - Spoken Languages (at least 1 language): 10%
            - Hourly Rate set (> 0 INR): 5%
            - Profile Photo uploaded: 10%
        """
        score = 0

        # Base identity
        if user.full_name and user.email and user.phone:
            score += 30

        # Bio
        if profile.bio and len(profile.bio.strip()) >= 20:
            score += 15

        # Skills
        if profile.skills and len(profile.skills) > 0:
            score += 20

        # Experience
        if profile.experience_years and profile.experience_years > 0:
            score += 10

        # Languages
        if profile.languages and len(profile.languages) > 0:
            score += 10

        # Hourly rate
        if profile.hourly_rate is not None and profile.hourly_rate > 0:
            score += 5

        # Profile photo
        if profile.profile_photo_url and profile.profile_photo_url.strip():
            score += 10

        score = min(score, 100)
        is_completed = score >= 70
        return score, is_completed

    @classmethod
    async def get_or_create_profile(cls, user: User) -> WorkerProfile:
        """Fetch worker profile for user, creating one if missing."""
        profile = await WorkerRepository.get_by_user_id(user.id)
        if not profile:
            profile = await WorkerRepository.create_profile(user.id)
        return profile

    @classmethod
    def _build_response_dto(
        cls, user: User, profile: WorkerProfile, completion_pct: int, is_completed: bool
    ) -> WorkerProfileResponse:
        """Construct standard WorkerProfileResponse DTO."""
        return WorkerProfileResponse(
            id=str(profile.id),
            user_id=str(user.id),
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            role=user.role.value,
            profile_photo_url=profile.profile_photo_url,
            profile_photo_public_id=profile.profile_photo_public_id,
            bio=profile.bio,
            experience_years=profile.experience_years,
            skills=profile.skills,
            languages=profile.languages,
            working_radius_km=profile.working_radius_km,
            availability=profile.availability,
            hourly_rate=profile.hourly_rate,
            rating=profile.rating,
            review_count=profile.review_count,
            profile_completion_percentage=completion_pct,
            profile_completed=is_completed,
            is_verified=getattr(profile, "is_verified", False),
            current_location=profile.current_location.model_dump() if profile.current_location else None,
            current_location_updated_at=profile.current_location_updated_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    @classmethod
    async def get_worker_profile(cls, user: User) -> WorkerProfileResponse:
        """Retrieve full worker profile DTO for authenticated user."""
        profile = await cls.get_or_create_profile(user)
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)

        # Sync profile_completed flag if state changed
        if profile.profile_completed != is_completed:
            profile.profile_completed = is_completed
            await WorkerRepository.save_profile(profile)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def update_worker_profile(
        cls, user: User, payload: UpdateWorkerProfileRequest
    ) -> WorkerProfileResponse:
        """Update worker profile fields and optional user full_name."""
        profile = await cls.get_or_create_profile(user)

        # 1. Update User level fields if provided
        if payload.full_name is not None and payload.full_name.strip() != user.full_name:
            user.full_name = payload.full_name.strip()
            await user.save()

        # 2. Update WorkerProfile level fields
        if payload.bio is not None:
            profile.bio = payload.bio.strip() if payload.bio else None
        if payload.experience_years is not None:
            profile.experience_years = payload.experience_years
        if payload.skills is not None:
            profile.skills = await cls.validate_and_normalize_skills(payload.skills)
        if payload.languages is not None:
            profile.languages = payload.languages
        if payload.working_radius_km is not None:
            profile.working_radius_km = payload.working_radius_km
        if payload.availability is not None:
            profile.availability = payload.availability
        if payload.hourly_rate is not None:
            profile.hourly_rate = payload.hourly_rate

        # 3. Calculate new completion percentage
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        # 4. Save profile
        await WorkerRepository.save_profile(profile)
        logger.info("Updated worker profile for user_id=%s (completion=%d%%)", user.id, completion_pct)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def upload_profile_photo(cls, user: User, file: UploadFile) -> WorkerProfileResponse:
        """Validate, upload (or replace) worker profile photo in Cloudinary and update database."""
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

        await WorkerRepository.save_profile(profile)
        logger.info("Uploaded profile photo for worker user_id=%s (url=%s)", user.id, secure_url)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def delete_profile_photo(cls, user: User) -> WorkerProfileResponse:
        """Delete worker profile photo from Cloudinary and clear database reference."""
        profile = await cls.get_or_create_profile(user)

        if profile.profile_photo_public_id:
            CloudinaryService.delete_image(profile.profile_photo_public_id)

        profile.profile_photo_url = None
        profile.profile_photo_public_id = None

        # Recalculate completion percentage
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        await WorkerRepository.save_profile(profile)
        logger.info("Deleted profile photo for worker user_id=%s", user.id)

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def update_worker_location(
        cls, user: User, payload: UpdateWorkerLocationRequest
    ) -> WorkerProfileResponse:
        """Update worker's real-time GPS location as a GeoJSON Point."""
        profile = await cls.get_or_create_profile(user)

        now = datetime.now(timezone.utc)
        profile.current_location = GeoJSONPoint.from_lat_lng(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        profile.current_location_updated_at = now

        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)
        profile.profile_completed = is_completed

        await WorkerRepository.save_profile(profile)
        logger.info(
            "Updated location for worker user_id=%s (lat=%.6f, lng=%.6f, updated_at=%s)",
            user.id, payload.latitude, payload.longitude, now.isoformat(),
        )

        return cls._build_response_dto(user, profile, completion_pct, is_completed)

    @classmethod
    async def get_worker_dashboard_data(cls, user: User):
        """
        Aggregate worker profile availability, marketplace statistics, top recommendations,
        recent open jobs, and application summary counts into a single dashboard payload.
        """
        from app.application.service import JobApplicationService
        from app.marketplace.schemas import MarketplaceSortOption
        from app.marketplace.service import MarketplaceService
        from app.utils.enums import ApplicationStatus
        from app.worker.dashboard_schemas import (
            ApplicationsSummaryDTO,
            MarketplaceStatsDTO,
            WorkerDashboardResponse,
        )

        profile = await cls.get_or_create_profile(user)
        completion_pct, is_completed = cls.calculate_completion_percentage(user, profile)

        # 1. Fetch marketplace jobs
        mp_service = MarketplaceService()
        recent_res = await mp_service.list_marketplace_bookings(
            worker_profile=profile,
            sort_by=MarketplaceSortOption.NEWEST,
            page=1,
            page_size=5,
        )

        rec_res = await mp_service.list_marketplace_bookings(
            worker_profile=profile,
            sort_by=MarketplaceSortOption.RECOMMENDED,
            page=1,
            page_size=3,
        )

        # 2. Fetch worker applications counts
        app_service = JobApplicationService()
        w_apps = await app_service.list_worker_applications(
            worker_user=user, page=1, page_size=100
        )

        pending_count = sum(1 for a in w_apps.items if a.application_status == ApplicationStatus.PENDING)
        accepted_count = sum(1 for a in w_apps.items if a.application_status == ApplicationStatus.ACCEPTED)
        rejected_count = sum(1 for a in w_apps.items if a.application_status == ApplicationStatus.REJECTED)

        stats = MarketplaceStatsDTO(
            available_jobs=recent_res.total,
            recommended_jobs=sum(1 for item in rec_res.items if item.is_recommended),
            active_applications=pending_count,
        )

        app_summary = ApplicationsSummaryDTO(
            total=w_apps.total,
            pending=pending_count,
            accepted=accepted_count,
            rejected=rejected_count,
        )

        return WorkerDashboardResponse(
            worker_id=str(user.id),
            worker_name=user.full_name,
            availability=profile.availability,
            working_radius_km=profile.working_radius_km,
            profile_completed=is_completed,
            is_verified=getattr(profile, "is_verified", False),
            stats=stats,
            applications_summary=app_summary,
            recommended_jobs=rec_res.items,
            recent_jobs=recent_res.items,
        )
