"""
Booking API Router — customer booking endpoints.

All endpoints:
    - Require authenticated customer role (CustomerDep).
    - Follow Router → Service → Repository → Model pattern.
    - No business logic in this file.

Endpoints:
    POST   /bookings              Create a new booking
    GET    /bookings              List customer's bookings (paginated)
    GET    /bookings/{id}         Get a single booking by ID
"""

import logging

from fastapi import APIRouter, Query, status

from datetime import date

from app.booking.scheduling import AvailableSlotsResponse
from app.booking.schemas import BookingListResponse, BookingResponse, CreateBookingRequest
from app.booking.service import BookingService
from app.core.dependencies import CustomerDep

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /bookings — Create booking
# ---------------------------------------------------------------------------

@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new booking",
    description=(
        "Create a new service booking for the authenticated customer. "
        "Validates that the service is active and the address belongs to the customer. "
        "Creates immutable snapshots of the service and address at booking time. "
        "Returns a booking with status PENDING and a unique booking number (KSYYYYnnnnn)."
    ),
)
async def create_booking(
    payload: CreateBookingRequest,
    current_user: CustomerDep,
) -> BookingResponse:
    """Create a new service booking."""
    return await BookingService.create_booking(current_user.id, payload)


# ---------------------------------------------------------------------------
# GET /bookings — List customer bookings
# ---------------------------------------------------------------------------

@router.get(
    "/bookings",
    response_model=BookingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List customer bookings",
    description=(
        "Retrieve all bookings for the authenticated customer, newest first. "
        "Optionally filter by status. Supports pagination via page and page_size. "
        "Customers only see their own bookings."
    ),
)
async def list_bookings(
    current_user: CustomerDep,
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by booking status (e.g., pending, cancelled).",
        examples=["pending"],
    ),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page (max 50)"),
) -> BookingListResponse:
    """List all bookings for the current customer."""
    skip = (page - 1) * page_size
    return await BookingService.list_bookings(
        current_user.id,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )


# ---------------------------------------------------------------------------
# GET /bookings/slots — Get available time slots for a date
# ---------------------------------------------------------------------------

@router.get(
    "/bookings/slots",
    response_model=AvailableSlotsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available booking time slots",
    description=(
        "Generate configurable booking time slots for a specified date (YYYY-MM-DD). "
        "Marks past slots as unavailable for today's bookings. "
        "Validates date is within the maximum advance booking window."
    ),
)
async def get_available_slots(
    current_user: CustomerDep,
    target_date: date = Query(
        ...,
        alias="date",
        description="Target booking date (YYYY-MM-DD)",
        examples=["2026-09-01"],
    ),
) -> AvailableSlotsResponse:
    """Get available time slots for a date."""
    return BookingService.get_available_slots(target_date)


# ---------------------------------------------------------------------------
# GET /bookings/{booking_id} — Get single booking
# ---------------------------------------------------------------------------

@router.get(
    "/bookings/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific booking",
    description=(
        "Fetch a single booking by its ObjectId. "
        "Returns 404 if the booking does not exist. "
        "Returns 403 if the booking belongs to a different customer."
    ),
)
async def get_booking(
    booking_id: str,
    current_user: CustomerDep,
) -> BookingResponse:
    """Get a single booking by ID for the current customer."""
    return await BookingService.get_booking(current_user.id, booking_id)
