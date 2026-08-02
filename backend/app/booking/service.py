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

from datetime import date
import logging

from beanie import PydanticObjectId

from app.address.models import Address
from app.auth.models import User
from app.booking.models import AddressSnapshot, Booking, ServiceSnapshot
from app.booking.repository import BookingRepository
from app.booking.schemas import (
    AddressSnapshotResponse,
    BookingListResponse,
    BookingResponse,
    CreateBookingRequest,
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

def _to_response(booking: Booking) -> BookingResponse:
    """
    Convert a Booking document to its response DTO.

    Extracts flat latitude/longitude from service_location GeoJSON
    (same pattern as the Address module) for Flutter compatibility.
    """
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
        assigned_at=booking.assigned_at.isoformat() if booking.assigned_at else None,
        started_at=booking.started_at.isoformat() if booking.started_at else None,
        completed_at=booking.completed_at.isoformat() if booking.completed_at else None,
        cancelled_at=booking.cancelled_at.isoformat() if booking.cancelled_at else None,
        cancellation_reason=booking.cancellation_reason,
        final_price=booking.final_price,
        inspection_id=str(booking.inspection_id) if booking.inspection_id else None,
        quotation_id=str(booking.quotation_id) if booking.quotation_id else None,
        payment_id=str(booking.payment_id) if booking.payment_id else None,
        created_at=booking.created_at.isoformat(),
        updated_at=booking.updated_at.isoformat(),
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
            customer_notes=payload.customer_notes,
            problem_description=payload.problem_description,
            problem_photos=payload.problem_photos,
        )

        booking = await BookingRepository.create(booking)
        logger.info(
            "Booking created: number=%s customer_id=%s service=%s",
            booking_number,
            customer_id,
            service.name,
        )
        return _to_response(booking)

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
        return _to_response(booking)

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
        dtos = [_to_response(b) for b in bookings]
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
