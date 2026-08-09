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
from pydantic import BaseModel, Field

from datetime import date, datetime

from app.booking.scheduling import AvailableSlotsResponse
from app.booking.schemas import BookingListResponse, BookingResponse, CreateBookingRequest
from app.booking.service import BookingService
from app.core.dependencies import CustomerDep
from app.auth.dependencies import ActiveUserDep

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


# ---------------------------------------------------------------------------
# Status Lifecycle Endpoints (Phase 4.7.1)
# ---------------------------------------------------------------------------

from app.auth.dependencies import ActiveUserDep, WorkerUserDep
from app.booking.schemas import BookingStatusResponse, UpdateBookingStatusRequest


@router.get(
    "/bookings/{booking_id}/status",
    response_model=BookingStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get booking status and next valid transitions",
    description="Inspect current booking status, allowed next statuses, and timestamp milestones.",
)
@router.get(
    "/customer/bookings/{booking_id}/status",
    response_model=BookingStatusResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_booking_status(
    booking_id: str,
    current_user: ActiveUserDep,
) -> BookingStatusResponse:
    """Get status inspection for a booking."""
    return await BookingService.get_booking_status(current_user, booking_id)


@router.put(
    "/worker/bookings/{booking_id}/status",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Update booking execution status (Worker only)",
    description="Assigned worker progresses the booking to the next valid execution status.",
)
@router.put(
    "/bookings/{booking_id}/status",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def update_booking_status_by_worker(
    booking_id: str,
    payload: UpdateBookingStatusRequest,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Update execution status for a booking."""
    return await BookingService.update_booking_status_by_worker(
        worker_user=current_user,
        booking_id=booking_id,
        new_status=payload.status,
        notes=payload.notes,
    )



# ---------------------------------------------------------------------------
# Worker Job Execution Specific Actions (Phase 4.7.2)
# ---------------------------------------------------------------------------

from app.booking.schemas import CompleteJobRequest


@router.get(
    "/worker/bookings",
    response_model=BookingListResponse,
    status_code=status.HTTP_200_OK,
    summary="List assigned bookings for worker",
    description=(
        "Return all bookings assigned to the authenticated worker (worker_id matches). "
        "Optionally filter by status. Supports pagination."
    ),
)
async def list_worker_bookings(
    current_user: WorkerUserDep,
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by booking status (e.g., assigned, in_progress).",
    ),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=50, description="Items per page (max 50)"),
) -> BookingListResponse:
    """List all bookings assigned to the authenticated worker."""
    return await BookingService.list_worker_bookings(
        current_user,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/worker/bookings/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assigned booking for worker",
    description="Retrieve full details for an assigned booking (Worker only).",
)
async def get_worker_booking(
    booking_id: str,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Get single assigned booking for worker."""
    return await BookingService.get_worker_booking(current_user, booking_id)


@router.put(
    "/worker/bookings/{booking_id}/start-travel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Start travel to customer location (ASSIGNED -> WORKER_EN_ROUTE)",
)
async def start_travel(
    booking_id: str,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Mark journey started."""
    return await BookingService.start_travel(current_user, booking_id)


@router.put(
    "/worker/bookings/{booking_id}/arrive",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark arrival at customer location (WORKER_EN_ROUTE -> ARRIVED)",
)
async def mark_arrived(
    booking_id: str,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Mark arrival at site."""
    return await BookingService.mark_arrived(current_user, booking_id)


@router.put(
    "/worker/bookings/{booking_id}/start-work",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Start service work execution (ARRIVED -> IN_PROGRESS)",
)
async def start_work(
    booking_id: str,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Mark work execution started."""
    return await BookingService.start_work(current_user, booking_id)


@router.put(
    "/worker/bookings/{booking_id}/complete",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete service work execution (IN_PROGRESS -> WORK_COMPLETED)",
)
async def complete_work(
    booking_id: str,
    payload: CompleteJobRequest,
    current_user: WorkerUserDep,
) -> BookingResponse:
    """Mark work execution completed with optional photos & notes."""
    return await BookingService.complete_work(current_user, booking_id, payload)


# ---------------------------------------------------------------------------
# Customer Confirmation & Acceptance Endpoints (Phase 4.7.3)
# ---------------------------------------------------------------------------

from app.booking.schemas import ConfirmCompletionRequest, CustomerCompletionReviewResponse


@router.get(
    "/customer/bookings/{booking_id}/completion",
    response_model=CustomerCompletionReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get completed work review payload for customer",
    description="Fetch before/after photos, completion notes, work summary, and actual duration for customer review.",
)
async def get_customer_completion_review(
    booking_id: str,
    current_user: CustomerDep,
) -> CustomerCompletionReviewResponse:
    """Fetch completed job review for customer."""
    return await BookingService.get_customer_completion_review(current_user, booking_id)


@router.put(
    "/customer/bookings/{booking_id}/confirm",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm service completion (WORK_COMPLETED -> CUSTOMER_CONFIRMED)",
    description="Customer reviews and accepts the completed service work.",
)
async def confirm_booking_completion(
    booking_id: str,
    payload: ConfirmCompletionRequest | None = None,
    current_user: CustomerDep = None,  # CustomerDep dependency
) -> BookingResponse:
    """Customer confirms service work completion."""
    notes = payload.notes if payload else None
    return await BookingService.confirm_booking_completion(current_user, booking_id, notes=notes)


# ---------------------------------------------------------------------------
# Timeline Audit Endpoints (Phase 4.7.4)
# ---------------------------------------------------------------------------

from app.booking.schemas import BookingTimelineResponse


@router.get(
    "/bookings/{booking_id}/timeline",
    response_model=BookingTimelineResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chronologically ordered booking timeline audit log",
    description="Fetch paginated timeline events logged for a booking (Customer, Assigned Worker, Admin).",
)
@router.get(
    "/customer/bookings/{booking_id}/timeline",
    response_model=BookingTimelineResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_booking_timeline(
    booking_id: str,
    current_user: ActiveUserDep,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=50, ge=1, le=100, description="Events per page (max 100)"),
) -> BookingTimelineResponse:
    """Fetch timeline audit events for a booking."""
    return await BookingService.get_booking_timeline(
        user=current_user,
        booking_id=booking_id,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# Chat Messages Endpoint
# ---------------------------------------------------------------------------

from app.booking.schemas import ChatMessageListResponse


@router.get(
    "/bookings/{booking_id}/messages",
    response_model=ChatMessageListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get chat messages for a booking",
    description="Retrieve all historical chat messages for a booking in chronological order.",
)
@router.get(
    "/customer/bookings/{booking_id}/messages",
    response_model=ChatMessageListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_booking_messages(
    booking_id: str,
    current_user: ActiveUserDep,
) -> ChatMessageListResponse:
    """Fetch historical chat messages for a booking."""
    return await BookingService.get_booking_messages(
        user_id=str(current_user.id),
        booking_id=booking_id,
    )


# ---------------------------------------------------------------------------
# Inspection Workflow Endpoints (Worker)
# ---------------------------------------------------------------------------

from app.auth.dependencies import WorkerUserDep
from pydantic import BaseModel


class ScheduleInspectionRequest(BaseModel):
    scheduled_at: datetime


@router.post(
    "/bookings/{booking_id}/inspection/accept",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept inspection visit",
    description="Worker accepts a site inspection request.",
)
async def accept_inspection(
    booking_id: str,
    worker: WorkerUserDep,
) -> BookingResponse:
    return await BookingService.accept_inspection(booking_id, worker)


@router.post(
    "/bookings/{booking_id}/inspection/schedule",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Schedule inspection visit date/time",
    description="Worker schedules the date and time for the site inspection visit.",
)
async def schedule_inspection(
    booking_id: str,
    payload: ScheduleInspectionRequest,
    worker: WorkerUserDep,
) -> BookingResponse:
    return await BookingService.schedule_inspection(booking_id, payload.scheduled_at, worker)


@router.post(
    "/bookings/{booking_id}/inspection/complete",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete inspection visit",
    description="Worker marks site inspection visit as finished.",
)
async def complete_inspection(
    booking_id: str,
    worker: WorkerUserDep,
) -> BookingResponse:
    return await BookingService.complete_inspection(booking_id, worker)


# ---------------------------------------------------------------------------
# Customer Applicant Review & Acceptance Endpoints (Phase 9)
# ---------------------------------------------------------------------------

from app.application.schemas import (
    CustomerApplicantItemResponse,
    CustomerApplicantListResponse,
)
from app.application.service import JobApplicationService


@router.get(
    "/bookings/{booking_id}/applicants",
    response_model=CustomerApplicantListResponse,
    status_code=status.HTTP_200_OK,
    summary="List worker applicants for a customer's booking",
    description="Fetch all worker applicants for a booking owned by the authenticated customer.",
)
@router.get(
    "/customer/bookings/{booking_id}/applicants",
    response_model=CustomerApplicantListResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_booking_applicants(
    booking_id: str,
    current_user: CustomerDep,
) -> CustomerApplicantListResponse:
    """List worker applicants for a booking owned by the authenticated customer."""
    app_service = JobApplicationService()
    return await app_service.list_booking_applicants_for_customer(current_user, booking_id)


@router.post(
    "/bookings/{booking_id}/applicants/{application_id}/accept",
    response_model=CustomerApplicantItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept worker applicant for a booking (Customer)",
    description="Customer accepts a specific worker applicant, assigning the worker to the booking and rejecting other applicants.",
)
@router.post(
    "/customer/bookings/{booking_id}/applicants/{application_id}/accept",
    response_model=CustomerApplicantItemResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def accept_booking_applicant(
    booking_id: str,
    application_id: str,
    current_user: CustomerDep,
) -> CustomerApplicantItemResponse:
    """Accept worker applicant for a booking owned by the authenticated customer."""
    app_service = JobApplicationService()
    return await app_service.accept_applicant_for_customer(current_user, booking_id, application_id)


# ---------------------------------------------------------------------------
# Booking Cancellation Endpoint
# ---------------------------------------------------------------------------

class CancelBookingRequest(BaseModel):
    reason: str | None = Field(default=None, description="Optional cancellation reason")


@router.post(
    "/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel a booking",
    description="Cancel a booking if it is in an eligible state.",
)
@router.post(
    "/customer/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
@router.put(
    "/bookings/{booking_id}/cancel",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def cancel_booking(
    booking_id: str,
    payload: CancelBookingRequest | None = None,
    current_user: ActiveUserDep = None,
) -> BookingResponse:
    """Cancel a booking."""
    reason = payload.reason if payload else None
    return await BookingService.cancel_booking(user=current_user, booking_id=booking_id, reason=reason)


