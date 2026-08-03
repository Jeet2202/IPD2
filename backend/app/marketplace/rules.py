"""
MarketplaceRulesEngine — centralized business rules and validation logic for worker marketplace.

Guarantees consistent marketplace behavior across search, discovery, scoring, and job applications.
"""

from app.application.models import JobApplication
from app.auth.models import User
from app.booking.models import Booking
from app.category.models import Service
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
)
from app.marketplace.recommendation.engine import calculate_haversine_distance
from app.utils.enums import BookingStatus, WorkerAvailability
from app.worker.models import WorkerProfile


class MarketplaceRulesEngine:
    """Centralized rules engine for the worker marketplace domain."""

    @staticmethod
    def validate_worker_eligibility(
        worker_user: User, worker_profile: WorkerProfile | None
    ) -> None:
        """
        Validate that a worker is eligible to participate in the marketplace.

        Rules:
            1. Account must be active (is_active == True).
            2. Profile must be completed (profile_completed == True).
            3. Availability must be set to AVAILABLE.
        """
        if not worker_user.is_active:
            raise ForbiddenException(
                message="Worker account is inactive and cannot participate in the marketplace",
                error_code="WORKER_INACTIVE",
            )

        if not worker_profile:
            raise ForbiddenException(
                message="Worker profile was not found. Please complete your registration.",
                error_code="WORKER_PROFILE_NOT_FOUND",
            )

        if hasattr(worker_profile, "profile_completed") and not worker_profile.profile_completed:
            raise ForbiddenException(
                message="Worker profile is incomplete. Please complete your profile to apply for marketplace jobs.",
                error_code="PROFILE_INCOMPLETE",
            )

        if worker_profile.availability != WorkerAvailability.AVAILABLE:
            raise BadRequestException(
                message=f"Worker must be set to AVAILABLE to participate in the marketplace (current status: '{worker_profile.availability.value}')",
                error_code="WORKER_NOT_AVAILABLE",
            )

    @staticmethod
    def is_booking_visible(
        booking: Booking,
        customer_user: User | None = None,
        service: Service | None = None,
    ) -> bool:
        """
        Determine if a booking should be visible in the marketplace listing.

        Rules:
            - Booking status MUST be PENDING.
            - Booking worker_id MUST be None (unassigned).
            - Customer user account (if checked) MUST be active.
            - Service (if checked) MUST be active.
        """
        if booking.status != BookingStatus.PENDING:
            return False

        if booking.worker_id is not None:
            return False

        if customer_user and not customer_user.is_active:
            return False

        if service and not service.is_active:
            return False

        return True

    @staticmethod
    def validate_application_submission(
        booking: Booking,
        worker_user: User,
        worker_profile: WorkerProfile | None,
        existing_application: JobApplication | None,
    ) -> None:
        """
        Validate all business rules for worker application submission.

        Rules:
            1. Worker eligibility (account active, profile completed, availability AVAILABLE).
            2. Booking availability (status PENDING, unassigned).
            3. No duplicate applications.
            4. GeoJSON service radius check.
        """
        # 1. Worker eligibility
        MarketplaceRulesEngine.validate_worker_eligibility(worker_user, worker_profile)

        # 2. Booking status & assignment check
        if not MarketplaceRulesEngine.is_booking_visible(booking):
            raise BadRequestException(
                message="Booking is no longer available for job applications",
                error_code="BOOKING_NOT_AVAILABLE",
            )

        # 3. Duplicate application check
        if existing_application:
            raise ConflictException(
                message="You have already submitted an application for this booking",
                error_code="DUPLICATE_APPLICATION",
            )

        # 4. Service radius check
        if worker_profile and worker_profile.current_location and worker_profile.current_location.coordinates:
            b_loc = booking.service_location or booking.address_snapshot.location
            if b_loc and b_loc.coordinates:
                dist_km = calculate_haversine_distance(
                    worker_profile.current_location.latitude,
                    worker_profile.current_location.longitude,
                    b_loc.latitude,
                    b_loc.longitude,
                )
                if dist_km > worker_profile.working_radius_km:
                    raise BadRequestException(
                        message=f"Booking location ({dist_km} km away) exceeds your working radius of {worker_profile.working_radius_km} km",
                        error_code="OUTSIDE_SERVICE_RADIUS",
                    )
