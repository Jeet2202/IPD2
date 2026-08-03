"""
Quotation FastAPI Router — worker and customer quotation endpoints foundation.
"""

from fastapi import APIRouter, Depends, Query, status

from app.auth.dependencies import ActiveUserDep, WorkerUserDep
from app.quotation.schemas import (
    AssignedWorkerResponse,
    CustomerQuotationResponse,
    QuotationAcceptResponse,
    QuotationCreateRequest,
    QuotationHistoryPaginatedResponse,
    QuotationPaginatedResponse,
    QuotationResponse,
    QuotationUpdateRequest,
)
from app.quotation.service import QuotationService
from app.utils.enums import QuotationStatus

router = APIRouter()


def get_quotation_service() -> QuotationService:
    return QuotationService()


@router.post(
    "/quotations",
    response_model=QuotationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a quotation for a job application",
    description="Worker submits or drafts a quotation for an applied marketplace booking.",
)
async def create_quotation(
    payload: QuotationCreateRequest,
    worker: WorkerUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationResponse:
    return await service.create_quotation(worker, payload)


@router.put(
    "/quotations/{quotation_id}",
    response_model=QuotationResponse,
    summary="Update or submit a draft quotation",
    description="Worker updates draft quotation details or submits the quotation.",
)
async def update_quotation(
    quotation_id: str,
    payload: QuotationUpdateRequest,
    worker: WorkerUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationResponse:
    return await service.update_quotation(worker, quotation_id, payload)


@router.get(
    "/quotations/application/{application_id}",
    response_model=QuotationResponse | None,
    summary="Get quotation by application ID",
    description="Returns quotation created for a specific job application.",
)
async def get_quotation_by_application(
    application_id: str,
    user: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationResponse | None:
    return await service.get_quotation_by_application(user, application_id)


@router.get(
    "/quotations/worker",
    response_model=QuotationPaginatedResponse,
    summary="List worker quotations",
    description="Returns a paginated list of quotations created by the authenticated worker.",
)
async def list_worker_quotations(
    worker: WorkerUserDep,
    status: QuotationStatus | None = Query(default=None, description="Filter by quotation status"),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationPaginatedResponse:
    return await service.list_worker_quotations(
        worker, status=status, page=page, page_size=page_size
    )


@router.get(
    "/quotations/booking/{booking_id}",
    response_model=list[QuotationResponse],
    summary="List quotations for a booking",
    description="Returns all quotations submitted for a specific booking.",
)
async def list_booking_quotations(
    booking_id: str,
    user: ActiveUserDep,
    status: QuotationStatus | None = Query(default=None, description="Filter by status"),
    service: QuotationService = Depends(get_quotation_service),
) -> list[QuotationResponse]:
    return await service.list_booking_quotations(user, booking_id, status=status)


@router.get(
    "/quotations/{quotation_id}",
    response_model=QuotationResponse,
    summary="Get quotation details",
    description="Returns detailed information for a specific quotation.",
)
async def get_quotation_detail(
    quotation_id: str,
    user: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationResponse:
    return await service.get_quotation_detail(user, quotation_id)


# ── Customer Quotations Endpoints ───────────────────────────────────────────

@router.get(
    "/customer/bookings/{booking_id}/quotations",
    response_model=list[CustomerQuotationResponse],
    summary="List submitted quotations for a customer's booking",
    description="Returns all submitted worker quotations for a booking owned by the customer.",
)
async def list_customer_booking_quotations(
    booking_id: str,
    customer: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> list[CustomerQuotationResponse]:
    return await service.list_booking_quotations_for_customer(customer, booking_id)


@router.get(
    "/customer/quotations/{quotation_id}",
    response_model=CustomerQuotationResponse,
    summary="Get customer quotation details",
    description="Returns detailed quotation info including worker profile for a customer.",
)
async def get_customer_quotation_detail_route(
    quotation_id: str,
    customer: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> CustomerQuotationResponse:
    return await service.get_customer_quotation_detail(customer, quotation_id)


@router.post(
    "/customer/quotations/{quotation_id}/accept",
    response_model=QuotationAcceptResponse,
    summary="Accept worker quotation",
    description="Customer accepts a quotation, assigning the worker and updating status atomically.",
)
async def accept_quotation(
    quotation_id: str,
    customer: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationAcceptResponse:
    return await service.accept_quotation(customer, quotation_id)


@router.post(
    "/customer/quotations/{quotation_id}/reject",
    response_model=CustomerQuotationResponse,
    summary="Reject worker quotation",
    description="Customer explicitly rejects a worker quotation.",
)
async def reject_quotation(
    quotation_id: str,
    customer: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> CustomerQuotationResponse:
    return await service.reject_quotation(customer, quotation_id)


@router.get(
    "/customer/bookings/{booking_id}/assigned-worker",
    response_model=AssignedWorkerResponse,
    summary="Get assigned worker details",
    description="Returns assigned worker and accepted quotation for a customer booking.",
)
async def get_assigned_worker(
    booking_id: str,
    customer: ActiveUserDep,
    service: QuotationService = Depends(get_quotation_service),
) -> AssignedWorkerResponse:
    return await service.get_assigned_worker(customer, booking_id)


@router.get(
    "/customer/quotations/{quotation_id}/history",
    response_model=QuotationHistoryPaginatedResponse,
    summary="Get customer quotation audit history",
    description="Returns read-only chronological audit trail log entries for a customer's quotation.",
)
async def get_customer_quotation_history(
    quotation_id: str,
    customer: ActiveUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationHistoryPaginatedResponse:
    return await service.get_quotation_history(customer, quotation_id, page=page, page_size=page_size)


@router.get(
    "/worker/quotations/{quotation_id}/history",
    response_model=QuotationHistoryPaginatedResponse,
    summary="Get worker quotation audit history",
    description="Returns read-only chronological audit trail log entries for a worker's quotation.",
)
async def get_worker_quotation_history(
    quotation_id: str,
    worker: WorkerUserDep,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationHistoryPaginatedResponse:
    return await service.get_quotation_history(worker, quotation_id, page=page, page_size=page_size)
