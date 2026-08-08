"""
MarketplaceRulesEngine — centralized business rules and validation logic for worker marketplace.

Guarantees consistent marketplace behavior across search, discovery, scoring, and job applications.
"""

from datetime import date

from app.application.models import JobApplication
from app.application.repository import JobApplicationRepository
from app.auth.models import User
from app.booking.models import Booking
from app.booking.scheduling import has_time_overlap
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
    async def validate_application_submission(
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
            5. Scheduling conflict check — worker must not have any PENDING or ACCEPTED
               application (or an ACCEPTED/IN_PROGRESS booking) that overlaps the target
               booking's date+time window.
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

        # 5. Scheduling conflict check
        await MarketplaceRulesEngine._check_schedule_conflict(booking, worker_user)

    @staticmethod
    async def _check_schedule_conflict(
        target_booking: Booking,
        worker_user: User,
    ) -> None:
        """
        Raise ConflictException(SCHEDULING_CONFLICT) if the worker already has a
        PENDING or ACCEPTED application — or an ACCEPTED/IN_PROGRESS booking —
        that overlaps the target booking's date and time window.

        Rules:
            - If target_booking has no scheduled_date or no scheduled_time → skip (on-demand).
            - Existing applications with status REJECTED or WITHDRAWN do NOT block.
            - Time overlap is computed as half-open intervals: [s1, e1) overlaps [s2, e2)
              iff s1 < e2 AND s2 < e1 (touching = not overlapping).
            - Existing bookings/applications with null scheduled_date are skipped (on-demand).
        """
        # On-demand target booking — no conflict detection possible
        if target_booking.scheduled_date is None or target_booking.scheduled_time is None:
            return

        target_date: date = target_booking.scheduled_date
        target_time: str = target_booking.scheduled_time

        # --- Check 1: Active applications (PENDING or ACCEPTED) ---
        active_apps = await JobApplicationRepository.find_active_applications_for_worker(
            worker_user.id
        )
        for app in active_apps:
            # Skip the application for THIS same booking (duplicate check already handled above)
            if app.booking_id == target_booking.id:
                continue

            linked_booking = await Booking.get(app.booking_id)
            if linked_booking is None:
                continue  # Booking deleted — skip
            if linked_booking.scheduled_date is None or linked_booking.scheduled_time is None:
                continue  # Linked booking is on-demand — skip

            if (
                linked_booking.scheduled_date == target_date
                and has_time_overlap(linked_booking.scheduled_time, target_time)
            ):
                raise ConflictException(
                    message=(
                        "You already have an active application for a job on the same date and "
                        "time slot. Please check your schedule or wait for your existing "
                        "application to be rejected before applying here."
                    ),
                    error_code="SCHEDULING_CONFLICT",
                )

        # --- Check 2: Direct bookings assigned to the worker (ACCEPTED / IN_PROGRESS) ---
        committed_statuses = [BookingStatus.ACCEPTED, BookingStatus.IN_PROGRESS]
        for status_val in committed_statuses:
            committed = await Booking.find(
                {
                    "worker_id": worker_user.id,
                    "status": status_val.value,
                    "scheduled_date": {"$ne": None},
                    "scheduled_time": {"$ne": None},
                }
            ).to_list()

            for committed_booking in committed:
                if committed_booking.scheduled_date is None or committed_booking.scheduled_time is None:
                    continue  # Extra guard for None
                if (
                    committed_booking.scheduled_date == target_date
                    and has_time_overlap(committed_booking.scheduled_time, target_time)
                ):
                    raise ConflictException(
                        message=(
                            "You already have an accepted booking on the same date and time slot. "
                            "Complete or cancel your existing booking before applying here."
                        ),
                        error_code="SCHEDULING_CONFLICT",
                    )
