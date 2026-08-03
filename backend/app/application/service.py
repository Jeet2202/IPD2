"""
JobApplication Service — business logic for worker job applications.

Business Rules:
    - Workers can express interest in marketplace bookings.
    - Applying DOES NOT assign the worker or change Booking.status from PENDING.
    - Duplicate applications for the same booking are rejected (409 DUPLICATE_APPLICATION).
    - Inactive workers or closed/assigned bookings are rejected (400 BOOKING_NOT_AVAILABLE).
    - Workers can only view their own applications (403 FORBIDDEN on unauthorized access).
"""

import math
from beanie import PydanticObjectId

from app.application.models import JobApplication
from app.application.repository import JobApplicationRepository
from app.application.schemas import (
    JobApplicationCreateRequest,
    JobApplicationPaginatedResponse,
    JobApplicationResponse,
)
from app.auth.models import User
from app.booking.models import Booking
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.marketplace.rules import MarketplaceRulesEngine
from app.utils.enums import ApplicationStatus, BookingStatus
from app.worker.models import WorkerProfile


class JobApplicationService:
    """Business logic for worker job applications."""

    def __init__(self, repo: JobApplicationRepository | None = None) -> None:
        self.repo = repo or JobApplicationRepository()

    async def _to_response_dto(
        self, application: JobApplication, booking: Booking | None = None
    ) -> JobApplicationResponse:
        """Map a JobApplication document to a response DTO with booking context."""
        if not booking:
            booking = await Booking.get(application.booking_id)

        if not booking:
            # Fallback for deleted booking context
            return JobApplicationResponse(
                id=str(application.id),
                booking_id=str(application.booking_id),
                worker_id=str(application.worker_id),
                application_status=application.application_status,
                cover_letter=application.cover_letter,
                proposed_price=application.proposed_price,
                booking_number="DELETED",
                service_name="Unknown Service",
                category_slug="unknown",
                booking_type=BookingStatus.PENDING,  # type fallback
                booking_status=BookingStatus.CANCELLED,
                scheduled_date=None,
                estimated_price=None,
                applied_at=application.applied_at,
            )

        return JobApplicationResponse(
            id=str(application.id),
            booking_id=str(application.booking_id),
            worker_id=str(application.worker_id),
            application_status=application.application_status,
            cover_letter=application.cover_letter,
            proposed_price=application.proposed_price,
            booking_number=booking.booking_number,
            service_name=booking.service_snapshot.name,
            category_slug=booking.service_snapshot.category_slug,
            booking_type=booking.booking_type,
            booking_status=booking.status,
            scheduled_date=booking.scheduled_date,
            estimated_price=booking.estimated_price,
            applied_at=application.applied_at,
        )

    async def apply_for_job(
        self, worker_user: User, request: JobApplicationCreateRequest
    ) -> JobApplicationResponse:
        """
        Submit a new worker application for an open marketplace booking.
        Delegates validation to centralized MarketplaceRulesEngine.
        """
        # 1. Validate booking ObjectId string
        if not PydanticObjectId.is_valid(request.booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{request.booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )
        booking_obj_id = PydanticObjectId(request.booking_id)

        # 2. Fetch booking
        booking = await Booking.get(booking_obj_id)
        if not booking:
            raise BadRequestException(
                message="Booking is no longer available for job applications",
                error_code="BOOKING_NOT_AVAILABLE",
            )

        # 3. Fetch WorkerProfile
        worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == worker_user.id)

        # 4. Fetch existing application
        existing = await self.repo.find_application_by_booking_and_worker(
            booking_obj_id, worker_user.id
        )

        # 5. Centralized Business Rules Validation
        MarketplaceRulesEngine.validate_application_submission(
            booking=booking,
            worker_user=worker_user,
            worker_profile=worker_profile,
            existing_application=existing,
        )

        # 6. Insert JobApplication document (Booking status REMAINS PENDING!)
        application = JobApplication(
            booking_id=booking_obj_id,
            worker_id=worker_user.id,
            application_status=ApplicationStatus.PENDING,
            cover_letter=request.cover_letter,
            proposed_price=request.proposed_price,
        )
        await self.repo.create_application(application)

        return await self._to_response_dto(application, booking)

    async def list_worker_applications(
        self,
        worker_user: User,
        status: ApplicationStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> JobApplicationPaginatedResponse:
        """
        List applications submitted by the authenticated worker.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        apps, total = await self.repo.list_applications_by_worker(
            worker_id=worker_user.id,
            status=status,
            skip=skip,
            limit=page_size,
        )

        dtos = [await self._to_response_dto(app) for app in apps]
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return JobApplicationPaginatedResponse(
            items=dtos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_worker_application_detail(
        self, worker_user: User, application_id: str
    ) -> JobApplicationResponse:
        """
        Get details of a specific job application.
        Strictly enforces that workers can only view their own applications.
        """
        application = await self.repo.get_application_by_id(application_id)
        if not application:
            raise NotFoundException(
                message=f"Job application '{application_id}' not found",
                error_code="APPLICATION_NOT_FOUND",
            )

        if application.worker_id != worker_user.id:
            raise ForbiddenException(
                message="You are not authorized to view this job application",
                error_code="UNAUTHORIZED_APPLICATION_ACCESS",
            )

        return await self._to_response_dto(application)
