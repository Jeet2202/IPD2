"""
Booking Service — business logic for booking creation and retrieval.

Business rules enforced here (NOT in router, NOT in repository):
    1. Service must exist and be active.
    2. Address must belong to the authenticated customer.
    3. Address must not be soft-deleted.
    4. Snapshots are created server-side from live documents.
    5. GeoJSON Point is copied from address snapshot into service_location.
    6. Estimated price and duration are copied from the service snapshot.
    7. Ownership: customers may only access their own bookings.

Future phases will add rules for:
    - Worker availability validation (Phase 4.4.x)
    - Inspection scheduling (Phase 4.5)
    - Quotation approval (Phase 4.6)
    - Payment lifecycle (Phase 4.7)
"""

from datetime import date, datetime, timezone
import logging

from beanie import PydanticObjectId

from app.address.models import Address
from app.auth.models import User
from app.booking.config import BookingLifecycleConfig
from app.booking.models import AddressSnapshot, Booking, BookingTimelineEvent, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.booking.schemas import (
    AddressSnapshotResponse,
    BookingListResponse,
    BookingResponse,
    BookingStatusResponse,
    BookingTimelineEventResponse,
    BookingTimelineResponse,
    CompleteJobRequest,
    ConfirmCompletionRequest,
    CreateBookingRequest,
    CustomerCompletionReviewResponse,
    ServiceSnapshotResponse,
)
from app.booking.scheduling import (
    AvailableSlotsResponse,
    generate_time_slots_for_date,
    validate_booking_schedule,
)
from app.category.models import Service
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.utils.enums import BookingStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------------

async def _to_response(booking: Booking) -> BookingResponse:
    """
    Convert a Booking document to its response DTO.

    Extracts flat latitude/longitude from service_location GeoJSON
    (same pattern as the Address module) for Flutter compatibility.
    Also queries applicant_count from job_applications collection.
    """
    from app.application.models import JobApplication

    latitude: float | None = None
    longitude: float | None = None
    if booking.service_location is not None:
        longitude = booking.service_location.coordinates[0]  # GeoJSON: [lng, lat]
        latitude = booking.service_location.coordinates[1]

    # Build address snapshot response with flat lat/lng
    addr = booking.address_snapshot
    addr_location = addr.location
    addr_lat: float | None = None
    addr_lng: float | None = None
    if addr_location is not None:
        addr_lng = addr_location.coordinates[0]
        addr_lat = addr_location.coordinates[1]

    address_dto = AddressSnapshotResponse(
        address_id=addr.address_id,
        label=addr.label,
        full_name=addr.full_name,
        phone=addr.phone,
        address_line_1=addr.address_line_1,
        address_line_2=addr.address_line_2,
        landmark=addr.landmark,
        city=addr.city,
        state=addr.state,
        country=addr.country,
        postal_code=addr.postal_code,
        latitude=addr_lat,
        longitude=addr_lng,
    )

    svc = booking.service_snapshot
    service_dto = ServiceSnapshotResponse(
        service_id=svc.service_id,
        name=svc.name,
        category_id=svc.category_id,
        category_slug=svc.category_slug,
        base_market_price=svc.base_market_price,
        estimated_duration_minutes=svc.estimated_duration_minutes,
        is_inspection_required=svc.is_inspection_required,
    )

    timeline_dtos = [
        BookingTimelineEventResponse(
            event_id=e.event_id,
            event_type=getattr(e, "event_type", "STATUS_CHANGE"),
            status=e.status.value if hasattr(e.status, "value") else str(e.status),
            previous_status=(
                e.previous_status.value if hasattr(e.previous_status, "value") else str(e.previous_status)
            ) if e.previous_status else None,
            new_status=(
                e.new_status.value if hasattr(e.new_status, "value") else str(e.new_status)
            ) if e.new_status else (
                e.status.value if hasattr(e.status, "value") else str(e.status)
            ),
            title=e.title,
            description=e.description,
            actor_id=str(e.actor_id),
            actor_role=e.actor_role,
            timestamp=e.timestamp.isoformat() if e.timestamp else "",
            metadata=e.metadata or {},
        )
        for e in (booking.timeline or [])
    ]

    # Count how many workers have applied for this booking
    applicant_count = await JobApplication.find(
        {"booking_id": booking.id}
    ).count()

    worker_name: str | None = None
    worker_phone: str | None = None
    if booking.worker_id is not None:
        worker_user = await User.get(booking.worker_id)
        if worker_user:
            worker_name = worker_user.full_name
            worker_phone = worker_user.phone

    return BookingResponse(
        id=str(booking.id),
        booking_number=booking.booking_number,
        customer_id=str(booking.customer_id),
        booking_type=booking.booking_type.value,
        status=booking.status.value,
        service_snapshot=service_dto,
        address_snapshot=address_dto,
        latitude=latitude,
        longitude=longitude,
        scheduled_date=(
            booking.scheduled_date.isoformat() if booking.scheduled_date else None
        ),
        scheduled_time=booking.scheduled_time,
        estimated_price=booking.estimated_price,
        estimated_duration_minutes=booking.estimated_duration_minutes,
        customer_notes=booking.customer_notes,
        problem_description=booking.problem_description,
        problem_photos=booking.problem_photos,
        worker_id=str(booking.worker_id) if booking.worker_id else None,
        worker_name=worker_name,
        worker_phone=worker_phone,
        assigned_at=booking.assigned_at.isoformat() if booking.assigned_at else None,
        en_route_at=booking.en_route_at.isoformat() if booking.en_route_at else None,
        arrived_at=booking.arrived_at.isoformat() if booking.arrived_at else None,
        started_at=booking.started_at.isoformat() if booking.started_at else None,
        completed_at=booking.completed_at.isoformat() if booking.completed_at else None,
        cancelled_at=booking.cancelled_at.isoformat() if booking.cancelled_at else None,
        cancellation_reason=booking.cancellation_reason,
        final_price=booking.final_price,
        inspection_id=str(booking.inspection_id) if booking.inspection_id else None,
        quotation_id=str(booking.quotation_id) if booking.quotation_id else None,
        payment_id=str(booking.payment_id) if booking.payment_id else None,
        completion_notes=booking.completion_notes,
        work_summary=booking.work_summary,
        before_photos=booking.before_photos or [],
        after_photos=booking.after_photos or [],
        timeline=timeline_dtos,
        created_at=booking.created_at.isoformat(),
        updated_at=booking.updated_at.isoformat(),
        applicant_count=applicant_count,
    )


def _verify_ownership(booking: Booking, customer_id: str) -> None:
    """
    Raise ForbiddenException if booking does not belong to customer_id.

    Called before every read or write on a specific booking document.
    """
    if str(booking.customer_id) != customer_id:
        raise ForbiddenException(
            message="You do not have permission to access this booking.",
            error_code="BOOKING_ACCESS_DENIED",
        )


# ---------------------------------------------------------------------------
# Booking Service
# ---------------------------------------------------------------------------

class BookingService:
    """Business logic for all customer booking operations."""

    # ── Create ───────────────────────────────────────────────────────────────

    @classmethod
    async def create_booking(
        cls,
        customer_id: str,
        payload: CreateBookingRequest,
    ) -> BookingResponse:
        """
        Create a new booking after validating all business rules.

        Steps:
            1. Validate service exists and is active.
            2. Validate address exists, belongs to customer, not deleted.
            3. Build immutable service + address snapshots.
            4. Copy GeoJSON Point from address snapshot → service_location.
            5. Generate unique booking number.
            6. Persist and return.
        """
        # -1. Validate customer account is active
        try:
            user_oid = PydanticObjectId(customer_id)
        except Exception:
            raise ForbiddenException(
                message="Invalid customer account.",
                error_code="INVALID_CUSTOMER_ID",
            )
        user: User | None = await User.get(user_oid)
        if user is None:
            raise NotFoundException(
                message="Customer account not found.",
                error_code="CUSTOMER_NOT_FOUND",
            )
        if not user.is_active:
            raise ForbiddenException(
                message="Customer account is inactive or disabled.",
                error_code="ACCOUNT_INACTIVE",
            )

        # 0. Validate schedule & time slot
        validate_booking_schedule(payload.scheduled_date, payload.scheduled_time)

        # 1. Validate service
        try:
            service_oid = PydanticObjectId(payload.service_id)
        except Exception:
            raise NotFoundException(
                message="Service not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        service: Service | None = await Service.get(service_oid)
        if service is None:
            raise NotFoundException(
                message="Service not found.",
                error_code="SERVICE_NOT_FOUND",
            )
        if not service.is_active:
            raise NotFoundException(
                message="This service is currently unavailable.",
                error_code="SERVICE_INACTIVE",
            )

        # 2. Validate address
        try:
            address_oid = PydanticObjectId(payload.address_id)
        except Exception:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )

        address: Address | None = await Address.get(address_oid)
        if address is None or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        if str(address.customer_id) != customer_id:
            raise ForbiddenException(
                message="This address does not belong to your account.",
                error_code="ADDRESS_ACCESS_DENIED",
            )
        if address.location is None or not address.location.coordinates:
            raise BadRequestException(
                message="Selected address must have valid GPS coordinates/location.",
                error_code="INVALID_ADDRESS_LOCATION",
            )

        # 3. Build snapshots
        service_snapshot = ServiceSnapshot(
            service_id=str(service.id),
            name=service.name,
            category_id=service.category_id,
            category_slug=service.category_slug,
            base_market_price=service.base_market_price,
            estimated_duration_minutes=service.estimated_duration_minutes,
            is_inspection_required=service.is_inspection_required,
        )

        address_snapshot = AddressSnapshot(
            address_id=str(address.id),
            label=address.label.value,
            full_name=address.full_name,
            phone=address.phone,
            address_line_1=address.address_line_1,
            address_line_2=address.address_line_2,
            landmark=address.landmark,
            city=address.city,
            state=address.state,
            country=address.country,
            postal_code=address.postal_code,
            location=address.location,  # Copy GeoJSON Point as-is
        )

        # 4. Copy GeoJSON Point to top-level service_location for 2dsphere index
        service_location = address.location  # None if address had no GPS

        # 5. Generate unique booking number
        booking_number = await BookingRepository.generate_booking_number()

        # 6. Persist
        booking = Booking(
            booking_number=booking_number,
            customer_id=PydanticObjectId(customer_id),
            booking_type=payload.booking_type,
            status=BookingStatus.PENDING,
            service_snapshot=service_snapshot,
            address_snapshot=address_snapshot,
            service_location=service_location,
            scheduled_date=payload.scheduled_date,
            scheduled_time=payload.scheduled_time,
            estimated_price=service.base_market_price,
            estimated_duration_minutes=service.estimated_duration_minutes,
            problem_photos=payload.problem_photos,
        )

        now_utc = datetime.now(timezone.utc)
        initial_event = BookingTimelineEvent(
            event_id=str(PydanticObjectId()),
            event_type="BOOKING_CREATED",
            status=BookingStatus.PENDING,
            previous_status=None,
            new_status=BookingStatus.PENDING,
            title="Booking Created",
            description=f"Service booking created for {service.name}",
            actor_id=PydanticObjectId(customer_id),
            actor_role="customer",
            timestamp=now_utc,
        )
        booking.timeline = [initial_event]

        booking = await BookingRepository.create(booking)
        logger.info(
            "Booking created: number=%s customer_id=%s service=%s",
            booking_number,
            customer_id,
            service.name,
        )
        return await _to_response(booking)

    # ── Get Single ───────────────────────────────────────────────────────────

    @classmethod
    async def get_booking(
        cls,
        customer_id: str,
        booking_id: str,
    ) -> BookingResponse:
        """
        Fetch a single booking by ID.

        Raises:
            NotFoundException: booking not found.
            ForbiddenException: booking belongs to a different customer.
        """
        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )
        _verify_ownership(booking, customer_id)
        return await _to_response(booking)

    # ── List ─────────────────────────────────────────────────────────────────

    @classmethod
    async def list_bookings(
        cls,
        customer_id: str,
        *,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> BookingListResponse:
        """
        Return paginated bookings for the authenticated customer.

        Args:
            customer_id: Current customer's User ID.
            status:      Optional status filter.
            skip:        Pagination offset.
            limit:       Page size (capped at 50 in router).
        """
        bookings = await BookingRepository.list_by_customer(
            customer_id, status=status, skip=skip, limit=limit
        )
        total = await BookingRepository.count_by_customer(
            customer_id, status=status
        )
        import asyncio
        dtos = list(await asyncio.gather(*[_to_response(b) for b in bookings]))
        return BookingListResponse(total=total, bookings=dtos)

    @classmethod
    async def list_worker_bookings(
        cls,
        worker_user: User,
        *,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> BookingListResponse:
        """
        Return paginated bookings assigned to the authenticated worker.

        Excludes PENDING bookings (not yet assigned to anyone).
        Filters to only bookings where worker_id == current worker.
        """
        skip = (page - 1) * page_size
        bookings = await BookingRepository.list_by_worker(
            worker_user.id, status=status, skip=skip, limit=page_size
        )
        total = await BookingRepository.count_by_worker(
            worker_user.id, status=status
        )
        import asyncio
        dtos = list(await asyncio.gather(*[_to_response(b) for b in bookings]))
        return BookingListResponse(total=total, bookings=dtos)

    # ── Available Slots ───────────────────────────────────────────────────────

    @classmethod
    def get_available_slots(cls, target_date: date) -> AvailableSlotsResponse:
        """
        Generate configurable time slots for a given date.

        Returns available/unavailable slots based on business hours, slot duration,
        max advance days, and same-day buffer rules.
        """
        return generate_time_slots_for_date(target_date)

    # ── Status Lifecycle Management (Phase 4.7.1) ────────────────────────────

    ALLOWED_TRANSITIONS = BookingLifecycleConfig.ALLOWED_TRANSITIONS

    @classmethod
    def validate_booking_mutable(cls, booking: Booking) -> None:
        """
        Ensure booking is not in a terminal state (CUSTOMER_CONFIRMED, COMPLETED, CANCELLED).
        Raises BadRequestException(BOOKING_TERMINATED) if terminal.
        """
        if booking.status in BookingLifecycleConfig.TERMINAL_STATUSES:
            raise BadRequestException(
                message=f"Operation rejected. Booking is in terminal status '{booking.status.value}'.",
                error_code="BOOKING_TERMINATED",
            )

    @classmethod
    def validate_status_transition(
        cls, current_status: BookingStatus, target_status: BookingStatus
    ) -> None:
        """
        Validate whether transitioning from current_status to target_status is allowed.

        Raises:
            BadRequestException: invalid, retrograde, skipping, or same status transition.
        """
        if current_status == target_status:
            raise BadRequestException(
                message=f"Booking is already in status '{current_status.value}'.",
                error_code="SAME_STATUS_TRANSITION",
            )

        if current_status in BookingLifecycleConfig.TERMINAL_STATUSES:
            raise BadRequestException(
                message=f"Cannot update status for a {current_status.value} booking.",
                error_code="BOOKING_TERMINATED",
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            allowed_names = [s.value for s in allowed]
            raise BadRequestException(
                message=(
                    f"Invalid status transition from '{current_status.value}' to '{target_status.value}'. "
                    f"Allowed next statuses: {allowed_names}"
                ),
                error_code="INVALID_STATUS_TRANSITION",
            )

    @classmethod
    async def update_booking_status_by_worker(
        cls,
        worker_user: User,
        booking_id: str,
        new_status: BookingStatus,
        notes: str | None = None,
    ) -> BookingResponse:
        """
        Worker status progression endpoint.

        Rules:
            1. Booking must exist.
            2. Worker user must be active and have worker role (or admin).
            3. Worker must be the assigned worker for this booking.
            4. Transition must be valid according to state machine.
            5. Timestamps update automatically based on milestone reach.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Worker role guard
        if worker_user.role not in ("worker", "admin"):
            raise ForbiddenException(
                message="Only assigned workers can update booking execution status.",
                error_code="WORKER_ROLE_REQUIRED",
            )

        # Check worker assignment
        is_assigned_worker = (
            booking.worker_id is not None
            and str(booking.worker_id) == str(worker_user.id)
        )
        if not is_assigned_worker and worker_user.role != "admin":
            raise ForbiddenException(
                message="You are not authorized to update status for a booking assigned to another worker.",
                error_code="UNAUTHORIZED_WORKER",
            )

        # Enforce transition rules
        cls.validate_status_transition(booking.status, new_status)

        prev_status = booking.status

        # Update status & timestamps
        booking.status = new_status
        now_utc = datetime.now(timezone.utc)

        if new_status in (BookingStatus.ASSIGNED, BookingStatus.ACCEPTED) and not booking.assigned_at:
            booking.assigned_at = now_utc
        elif new_status == BookingStatus.WORKER_EN_ROUTE and not booking.en_route_at:
            booking.en_route_at = now_utc
        elif new_status == BookingStatus.ARRIVED and not booking.arrived_at:
            booking.arrived_at = now_utc
        elif new_status == BookingStatus.IN_PROGRESS and not booking.started_at:
            booking.started_at = now_utc
        elif new_status in (BookingStatus.WORK_COMPLETED, BookingStatus.CUSTOMER_CONFIRMED, BookingStatus.COMPLETED) and not booking.completed_at:
            booking.completed_at = now_utc
        elif new_status == BookingStatus.CANCELLED and not booking.cancelled_at:
            booking.cancelled_at = now_utc

        # Record timeline event
        title_map = {
            BookingStatus.WORKER_EN_ROUTE: "Worker Started Journey",
            BookingStatus.ARRIVED: "Worker Arrived on Site",
            BookingStatus.IN_PROGRESS: "Work Started",
            BookingStatus.WORK_COMPLETED: "Work Completed",
            BookingStatus.CUSTOMER_CONFIRMED: "Customer Confirmed Work",
            BookingStatus.CANCELLED: "Booking Cancelled",
        }
        event_title = title_map.get(new_status, f"Status updated to {new_status.value.upper()}")
        event = BookingTimelineEvent(
            event_id=str(PydanticObjectId()),
            event_type=new_status.value.upper(),
            status=new_status,
            previous_status=prev_status,
            new_status=new_status,
            title=event_title,
            description=notes or f"Booking status changed to {new_status.value}",
            actor_id=worker_user.id,
            actor_role=worker_user.role,
            timestamp=now_utc,
        )
        if booking.timeline is None:
            booking.timeline = []
        booking.timeline.append(event)

        await booking.save()
        logger.info(
            "Booking status updated: id=%s number=%s new_status=%s worker_id=%s",
            booking_id,
            booking.booking_number,
            new_status.value,
            worker_user.id,
        )
        return await _to_response(booking)

    # ── Job Execution Flow Actions (Phase 4.7.2) ─────────────────────────────

    @classmethod
    async def start_travel(
        cls, worker_user: User, booking_id: str
    ) -> BookingResponse:
        """Worker marks journey started -> WORKER_EN_ROUTE."""
        return await cls.update_booking_status_by_worker(
            worker_user=worker_user,
            booking_id=booking_id,
            new_status=BookingStatus.WORKER_EN_ROUTE,
            notes="Worker is en route to customer location.",
        )

    @classmethod
    async def mark_arrived(
        cls, worker_user: User, booking_id: str
    ) -> BookingResponse:
        """Worker marks arrival at site -> ARRIVED."""
        return await cls.update_booking_status_by_worker(
            worker_user=worker_user,
            booking_id=booking_id,
            new_status=BookingStatus.ARRIVED,
            notes="Worker arrived at customer site.",
        )

    @classmethod
    async def start_work(
        cls, worker_user: User, booking_id: str
    ) -> BookingResponse:
        """Worker marks work execution started -> IN_PROGRESS."""
        return await cls.update_booking_status_by_worker(
            worker_user=worker_user,
            booking_id=booking_id,
            new_status=BookingStatus.IN_PROGRESS,
            notes="Worker began service execution.",
        )

    @classmethod
    async def complete_work(
        cls,
        worker_user: User,
        booking_id: str,
        payload: CompleteJobRequest,
    ) -> BookingResponse:
        """
        Worker marks work completed -> WORK_COMPLETED.

        Stores optional before_photos, after_photos, completion_notes, work_summary.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Worker role guard
        if worker_user.role not in ("worker", "admin"):
            raise ForbiddenException(
                message="Only assigned workers can complete booking execution.",
                error_code="WORKER_ROLE_REQUIRED",
            )

        # Check worker assignment
        is_assigned_worker = (
            booking.worker_id is not None
            and str(booking.worker_id) == str(worker_user.id)
        )
        if not is_assigned_worker and worker_user.role != "admin":
            raise ForbiddenException(
                message="You are not authorized to update status for a booking assigned to another worker.",
                error_code="UNAUTHORIZED_WORKER",
            )

        # Save completion payload details prior to status validation & save
        if payload.completion_notes:
            booking.completion_notes = payload.completion_notes
        if payload.work_summary:
            booking.work_summary = payload.work_summary
        if payload.before_photos:
            booking.before_photos = payload.before_photos
        if payload.after_photos:
            booking.after_photos = payload.after_photos

        await booking.save()

        return await cls.update_booking_status_by_worker(
            worker_user=worker_user,
            booking_id=booking_id,
            new_status=BookingStatus.WORK_COMPLETED,
            notes=payload.completion_notes or "Work completed successfully by worker.",
        )

    @classmethod
    async def get_worker_booking(
        cls, worker_user: User, booking_id: str
    ) -> BookingResponse:
        """Fetch assigned booking details for worker."""
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Guard: worker must be assigned worker or admin
        is_assigned_worker = (
            booking.worker_id is not None
            and str(booking.worker_id) == str(worker_user.id)
        )
        if not is_assigned_worker and worker_user.role != "admin":
            raise ForbiddenException(
                message="You do not have permission to access this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        return await _to_response(booking)

    @classmethod
    async def get_booking_status(
        cls,
        user: User,
        booking_id: str,
    ) -> BookingStatusResponse:
        """
        Inspect current status, allowed next statuses, and timestamps for a booking.

        Accessible by customer owner, assigned worker, or admin.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Ownership guard
        is_customer_owner = str(booking.customer_id) == str(user.id)
        is_assigned_worker = booking.worker_id is not None and str(booking.worker_id) == str(user.id)
        is_admin = user.role == "admin"

        if not (is_customer_owner or is_assigned_worker or is_admin):
            raise ForbiddenException(
                message="You are not authorized to view the status of this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        allowed = cls.ALLOWED_TRANSITIONS.get(booking.status, [])
        next_statuses = [s.value for s in allowed]

        timestamps = {
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "assigned_at": booking.assigned_at.isoformat() if booking.assigned_at else None,
            "started_at": booking.started_at.isoformat() if booking.started_at else None,
            "completed_at": booking.completed_at.isoformat() if booking.completed_at else None,
            "cancelled_at": booking.cancelled_at.isoformat() if booking.cancelled_at else None,
        }

        return BookingStatusResponse(
            booking_id=str(booking.id),
            booking_number=booking.booking_number,
            current_status=booking.status.value,
            next_allowed_statuses=next_statuses,
            assigned_worker_id=str(booking.worker_id) if booking.worker_id else None,
            timestamps=timestamps,
        )

    # ── Customer Confirmation & Acceptance (Phase 4.7.3) ──────────────────────

    @classmethod
    async def get_customer_completion_review(
        cls,
        customer_user: User,
        booking_id: str,
    ) -> CustomerCompletionReviewResponse:
        """
        Fetch completed work review payload for customer before confirmation.

        Rules:
            1. Booking must exist.
            2. Customer must be the booking owner.
            3. Booking must be in WORK_COMPLETED or CUSTOMER_CONFIRMED status.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        _verify_ownership(booking, str(customer_user.id))

        if booking.status not in (
            BookingStatus.WORK_COMPLETED,
            BookingStatus.CUSTOMER_CONFIRMED,
            BookingStatus.COMPLETED,
        ):
            raise BadRequestException(
                message=f"Completion review unavailable. Booking status is '{booking.status.value}'.",
                error_code="BOOKING_NOT_WORK_COMPLETED",
            )

        actual_duration: int | None = None
        if booking.started_at and booking.completed_at:
            diff_sec = (booking.completed_at - booking.started_at).total_seconds()
            actual_duration = max(1, int(diff_sec // 60))

        timeline_dtos = [
            BookingTimelineEventResponse(
                event_id=e.event_id,
                status=e.status.value if hasattr(e.status, "value") else str(e.status),
                title=e.title,
                description=e.description,
                actor_id=str(e.actor_id),
                actor_role=e.actor_role,
                timestamp=e.timestamp.isoformat() if e.timestamp else "",
                metadata=e.metadata or {},
            )
            for e in (booking.timeline or [])
        ]

        return CustomerCompletionReviewResponse(
            booking_id=str(booking.id),
            booking_number=booking.booking_number,
            service_name=booking.service_snapshot.name,
            status=booking.status.value,
            worker_id=str(booking.worker_id) if booking.worker_id else None,
            estimated_duration_minutes=booking.estimated_duration_minutes,
            started_at=booking.started_at.isoformat() if booking.started_at else None,
            completed_at=booking.completed_at.isoformat() if booking.completed_at else None,
            actual_duration_minutes=actual_duration,
            completion_notes=booking.completion_notes,
            work_summary=booking.work_summary,
            before_photos=booking.before_photos or [],
            after_photos=booking.after_photos or [],
            timeline=timeline_dtos,
        )

    @classmethod
    async def confirm_booking_completion(
        cls,
        customer_user: User,
        booking_id: str,
        notes: str | None = None,
    ) -> BookingResponse:
        """
        Customer confirms completed service -> CUSTOMER_CONFIRMED.

        Rules:
            1. Booking must exist.
            2. Customer must be the booking owner.
            3. Booking status MUST be WORK_COMPLETED.
            4. Automatically logs timeline event "Customer Confirmed Completion".
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        _verify_ownership(booking, str(customer_user.id))

        if booking.status in (BookingStatus.CUSTOMER_CONFIRMED, BookingStatus.COMPLETED):
            raise BadRequestException(
                message="Booking has already been confirmed by customer.",
                error_code="SAME_STATUS_TRANSITION",
            )

        if booking.status != BookingStatus.WORK_COMPLETED:
            raise BadRequestException(
                message=f"Cannot confirm completion for a booking in status '{booking.status.value}'. Worker must mark WORK_COMPLETED first.",
                error_code="BOOKING_NOT_WORK_COMPLETED",
            )

        booking.status = BookingStatus.CUSTOMER_CONFIRMED
        now_utc = datetime.now(timezone.utc)
        if not booking.completed_at:
            booking.completed_at = now_utc

        event = BookingTimelineEvent(
            event_id=str(PydanticObjectId()),
            status=BookingStatus.CUSTOMER_CONFIRMED,
            title="Customer Confirmed Completion",
            description=notes or "Customer reviewed and accepted the completed service.",
            actor_id=customer_user.id,
            actor_role=customer_user.role,
            timestamp=now_utc,
        )
        if booking.timeline is None:
            booking.timeline = []
        booking.timeline.append(event)

        await booking.save()
        logger.info(
            "Booking completion confirmed by customer: id=%s number=%s customer_id=%s",
            booking_id,
            booking.booking_number,
            customer_user.id,
        )
        return await _to_response(booking)

    # ── Timeline Audit Log (Phase 4.7.4) ─────────────────────────────────────

    @classmethod
    async def get_booking_timeline(
        cls,
        user: User,
        booking_id: str,
        page: int = 1,
        page_size: int = 50,
    ) -> BookingTimelineResponse:
        """
        Fetch chronologically ordered, paginated timeline audit log for a booking.

        Rules:
            1. Booking must exist.
            2. User must be customer owner, assigned worker, or admin.
            3. Chronological sorting (timestamp ascending).
            4. Paginated result.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Ownership guard
        is_customer_owner = str(booking.customer_id) == str(user.id)
        is_assigned_worker = booking.worker_id is not None and str(booking.worker_id) == str(user.id)
        is_admin = user.role == "admin"

        if not (is_customer_owner or is_assigned_worker or is_admin):
            raise ForbiddenException(
                message="You are not authorized to view the timeline for this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        raw_events = booking.timeline or []
        sorted_events = sorted(raw_events, key=lambda e: e.timestamp or datetime.min.replace(tzinfo=timezone.utc))

        total_events = len(sorted_events)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_events = sorted_events[start_idx:end_idx]

        event_dtos = [
            BookingTimelineEventResponse(
                event_id=e.event_id,
                event_type=getattr(e, "event_type", "STATUS_CHANGE"),
                status=e.status.value if hasattr(e.status, "value") else str(e.status),
                previous_status=(
                    e.previous_status.value if hasattr(e.previous_status, "value") else str(e.previous_status)
                ) if e.previous_status else None,
                new_status=(
                    e.new_status.value if hasattr(e.new_status, "value") else str(e.new_status)
                ) if e.new_status else (
                    e.status.value if hasattr(e.status, "value") else str(e.status)
                ),
                title=e.title,
                description=e.description,
                actor_id=str(e.actor_id),
                actor_role=e.actor_role,
                timestamp=e.timestamp.isoformat() if e.timestamp else "",
                metadata=e.metadata or {},
            )
            for e in paginated_events
        ]

        return BookingTimelineResponse(
            booking_id=str(booking.id),
            booking_number=booking.booking_number,
            current_status=booking.status.value,
            total_events=total_events,
            page=page,
            page_size=page_size,
            events=event_dtos,
        )

    # ── Cancellation Governance (Phase 4.7.5) ─────────────────────────────────

    @classmethod
    async def cancel_booking(
        cls,
        user: User,
        booking_id: str,
        reason: str | None = None,
    ) -> BookingResponse:
        """
        Cancel a booking (Customer owner, Assigned Worker, or Admin).

        Rules:
            1. Booking must exist.
            2. User must be customer owner, assigned worker, or admin.
            3. Booking status MUST be in CANCELLATION_ALLOWED_STATUSES.
            4. Automatically records "Booking Cancelled" timeline event.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        booking = await BookingRepository.get_by_id(booking_id)
        if booking is None:
            raise NotFoundException(
                message="Booking not found.",
                error_code="BOOKING_NOT_FOUND",
            )

        # Ownership guard
        is_customer_owner = str(booking.customer_id) == str(user.id)
        is_assigned_worker = booking.worker_id is not None and str(booking.worker_id) == str(user.id)
        is_admin = user.role == "admin"

        if not (is_customer_owner or is_assigned_worker or is_admin):
            raise ForbiddenException(
                message="You are not authorized to cancel this booking.",
                error_code="BOOKING_ACCESS_DENIED",
            )

        cls.validate_booking_mutable(booking)

        if booking.status not in BookingLifecycleConfig.CANCELLATION_ALLOWED_STATUSES:
            raise BadRequestException(
                message=f"Cannot cancel booking in current status '{booking.status.value}'.",
                error_code="INVALID_STATUS_TRANSITION",
            )

        prev_status = booking.status
        booking.status = BookingStatus.CANCELLED
        now_utc = datetime.now(timezone.utc)
        booking.cancelled_at = now_utc
        booking.cancellation_reason = reason

        event = BookingTimelineEvent(
            event_id=str(PydanticObjectId()),
            event_type="CANCELLED",
            status=BookingStatus.CANCELLED,
            previous_status=prev_status,
            new_status=BookingStatus.CANCELLED,
            title="Booking Cancelled",
            description=reason or f"Booking cancelled by {user.role}.",
            actor_id=user.id,
            actor_role=user.role,
            timestamp=now_utc,
        )
        if booking.timeline is None:
            booking.timeline = []
        booking.timeline.append(event)

        await booking.save()
        logger.info(
            "Booking cancelled: id=%s number=%s user_id=%s role=%s",
            booking_id,
            booking.booking_number,
            user.id,
            user.role,
        )
        return await _to_response(booking)




