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

from datetime import datetime, timezone

from app.application.models import JobApplication
from app.application.repository import JobApplicationRepository
from app.application.schemas import (
    CustomerApplicantItemResponse,
    CustomerApplicantListResponse,
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
from app.utils.enums import ApplicationStatus, BookingStatus, BookingType
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
                booking_type=BookingType.NORMAL_SERVICE,  # type fallback
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
        await MarketplaceRulesEngine.validate_application_submission(
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

    async def list_booking_applicants_for_customer(
        self, customer_user: User, booking_id: str
    ) -> CustomerApplicantListResponse:
        """
        List all worker applicants for a booking owned by the authenticated customer.
        Strictly enforces customer ownership authorization.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )
        b_oid = PydanticObjectId(booking_id)
        booking = await Booking.get(b_oid)
        if not booking:
            raise NotFoundException(
                message="Booking not found",
                error_code="BOOKING_NOT_FOUND",
            )

        # Ownership authorization: only customer who created booking (or admin) can view applicants
        if booking.customer_id != customer_user.id and getattr(customer_user, "role", None) != "admin":
            raise ForbiddenException(
                message="You are not authorized to view applicants for this booking",
                error_code="BOOKING_NOT_OWNED",
            )

        applications = await JobApplication.find(
            JobApplication.booking_id == b_oid
        ).sort("-applied_at").to_list()

        applicant_dtos = []
        for app in applications:
            w_user = await User.get(app.worker_id)
            w_profile = await WorkerProfile.find_one(WorkerProfile.user_id == app.worker_id)

            w_name = w_user.full_name if w_user else "Worker"
            w_phone = w_user.phone if w_user else None
            w_avatar = getattr(w_profile, "avatar_url", None) if w_profile else None
            w_skills = getattr(w_profile, "skills", []) if w_profile else []
            w_radius = getattr(w_profile, "working_radius_km", 10.0) if w_profile else 10.0

            applicant_dtos.append(
                CustomerApplicantItemResponse(
                    application_id=str(app.id),
                    booking_id=str(app.booking_id),
                    worker_id=str(app.worker_id),
                    worker_name=w_name,
                    worker_phone=w_phone,
                    worker_avatar_url=w_avatar,
                    worker_skills=w_skills,
                    working_radius_km=w_radius,
                    cover_letter=app.cover_letter,
                    proposed_price=app.proposed_price,
                    application_status=app.application_status,
                    applied_at=app.applied_at,
                )
            )

        return CustomerApplicantListResponse(
            booking_id=str(booking.id),
            booking_number=booking.booking_number,
            booking_status=booking.status,
            applicant_count=len(applicant_dtos),
            applicants=applicant_dtos,
        )

    async def accept_applicant_for_customer(
        self, customer_user: User, booking_id: str, application_id: str
    ) -> CustomerApplicantItemResponse:
        """
        Customer accepts a specific worker applicant for their booking.
        Enforces:
            1. Customer ownership of booking.
            2. Booking availability (PENDING, unassigned).
            3. Target application belongs to booking and is PENDING.
            4. Re-validates worker eligibility at acceptance time (active worker, skill match, working radius match).
            5. Atomic MongoDB booking assignment to prevent race conditions.
            6. Transitions target application to ACCEPTED and all other pending applications for this booking to REJECTED.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )
        if not PydanticObjectId.is_valid(application_id):
            raise BadRequestException(
                message=f"Invalid application ID format '{application_id}'",
                error_code="INVALID_APPLICATION_ID",
            )

        b_oid = PydanticObjectId(booking_id)
        app_oid = PydanticObjectId(application_id)

        # 1. Fetch booking
        booking = await Booking.get(b_oid)
        if not booking:
            raise NotFoundException(
                message="Booking not found",
                error_code="BOOKING_NOT_FOUND",
            )

        # 2. Customer ownership authorization
        if booking.customer_id != customer_user.id and getattr(customer_user, "role", None) != "admin":
            raise ForbiddenException(
                message="You are not authorized to accept applicants for this booking",
                error_code="BOOKING_NOT_OWNED",
            )

        # 3. Check booking availability
        if booking.status != BookingStatus.PENDING or booking.worker_id is not None:
            raise BadRequestException(
                message="Booking is no longer available for worker assignment",
                error_code="BOOKING_NOT_AVAILABLE",
            )

        # 4. Fetch target application
        target_app = await JobApplication.get(app_oid)
        if not target_app or target_app.booking_id != b_oid:
            raise NotFoundException(
                message="Applicant record not found for this booking",
                error_code="APPLICATION_NOT_FOUND",
            )

        if target_app.application_status != ApplicationStatus.PENDING:
            if target_app.application_status == ApplicationStatus.ACCEPTED and booking.worker_id == target_app.worker_id:
                # Idempotent response if already accepted for this worker
                pass
            else:
                raise BadRequestException(
                    message=f"Cannot accept application with status '{target_app.application_status.value}'",
                    error_code="APPLICATION_NOT_PENDING",
                )

        # 5. Server-side worker eligibility revalidation at acceptance time
        worker_user = await User.get(target_app.worker_id)
        if not worker_user or not worker_user.is_active:
            raise BadRequestException(
                message="Worker account is inactive or no longer available",
                error_code="WORKER_NOT_AVAILABLE",
            )

        worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == target_app.worker_id)
        MarketplaceRulesEngine.validate_worker_acceptance_eligibility(booking, worker_user, worker_profile)

        # 6. Atomic MongoDB Booking Assignment (Race Condition Protection)
        now = datetime.now(timezone.utc)
        collection = Booking.get_motor_collection()
        res = await collection.update_one(
            {
                "_id": b_oid,
                "worker_id": None,
                "status": BookingStatus.PENDING.value,
            },
            {
                "$set": {
                    "worker_id": target_app.worker_id,
                    "status": BookingStatus.ASSIGNED.value,
                    "assigned_at": now,
                    "updated_at": now,
                }
            },
        )

        if res.modified_count == 0:
            fresh_b = await Booking.get(b_oid)
            if fresh_b and fresh_b.worker_id is not None:
                raise ConflictException(
                    message="This booking has already been assigned to another worker",
                    error_code="BOOKING_ALREADY_ASSIGNED",
                )
            raise BadRequestException(
                message="Booking is no longer available for assignment",
                error_code="BOOKING_NOT_AVAILABLE",
            )

        # 7. Update target application to ACCEPTED
        target_app.application_status = ApplicationStatus.ACCEPTED
        await target_app.save()

        # 8. Update all other PENDING applications for this booking to REJECTED
        other_apps = await JobApplication.find(
            JobApplication.booking_id == b_oid,
            JobApplication.id != app_oid,
            JobApplication.application_status == ApplicationStatus.PENDING,
        ).to_list()

        for other_app in other_apps:
            other_app.application_status = ApplicationStatus.REJECTED
            await other_app.save()

        w_name = worker_user.full_name if worker_user else "Worker"
        w_phone = worker_user.phone if worker_user else None
        w_avatar = getattr(worker_profile, "avatar_url", None) if worker_profile else None
        w_skills = getattr(worker_profile, "skills", []) if worker_profile else []
        w_radius = getattr(worker_profile, "working_radius_km", 10.0) if worker_profile else 10.0

        return CustomerApplicantItemResponse(
            application_id=str(target_app.id),
            booking_id=str(target_app.booking_id),
            worker_id=str(target_app.worker_id),
            worker_name=w_name,
            worker_phone=w_phone,
            worker_avatar_url=w_avatar,
            worker_skills=w_skills,
            working_radius_km=w_radius,
            cover_letter=target_app.cover_letter,
            proposed_price=target_app.proposed_price,
            application_status=target_app.application_status,
            applied_at=target_app.applied_at,
        )
