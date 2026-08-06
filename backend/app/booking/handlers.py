"""
Booking Type Handlers — Strategy Pattern for Booking Creation (Open/Closed Principle).

Isolates domain logic for:
  - Standard Booking (Catalog Service)
  - Custom Service Booking (User-defined scope & budget)
  - Inspection Request Booking (Site-visit diagnostic & quotation prep)
"""

from abc import ABC, abstractmethod
from typing import Tuple

from beanie import PydanticObjectId

from app.address.models import Address
from app.booking.models import Booking, ServiceSnapshot, AddressSnapshot
from app.booking.schemas import CreateBookingRequest
from app.category.models import Service, ServiceCategory
from app.core.exceptions import BadRequestException, NotFoundException
from app.utils.enums import BookingStatus, BookingType, InspectionStatus


class BaseBookingHandler(ABC):
    """Abstract Strategy interface for building synthetic snapshots & booking models."""

    @abstractmethod
    async def build_service_snapshot_and_pricing(
        self, payload: CreateBookingRequest
    ) -> Tuple[ServiceSnapshot, float | None, int | None]:
        """Returns (ServiceSnapshot, estimated_price, estimated_duration_minutes)."""
        pass

    @abstractmethod
    def setup_booking_specific_fields(
        self, booking: Booking, payload: CreateBookingRequest
    ) -> None:
        """Mutate specific domain fields on booking (e.g. inspection_status, custom_title)."""
        pass


class StandardBookingHandler(BaseBookingHandler):
    """Handler for standard catalog service bookings."""

    async def build_service_snapshot_and_pricing(
        self, payload: CreateBookingRequest
    ) -> Tuple[ServiceSnapshot, float | None, int | None]:
        if not payload.service_id:
            raise BadRequestException(
                message="Service ID is required for standard bookings.",
                error_code="SERVICE_ID_REQUIRED",
            )
        try:
            service_oid = PydanticObjectId(payload.service_id)
        except Exception:
            raise NotFoundException(
                message="Service not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        service: Service | None = await Service.get(service_oid)
        if service is None or not service.is_active:
            raise NotFoundException(
                message="Service is inactive or unavailable.",
                error_code="SERVICE_UNAVAILABLE",
            )

        snapshot = ServiceSnapshot(
            service_id=str(service.id),
            name=service.name,
            category_id=service.category_id,
            category_slug=service.category_slug,
            base_market_price=service.base_market_price,
            estimated_duration_minutes=service.estimated_duration_minutes,
            is_inspection_required=service.is_inspection_required,
        )
        return snapshot, service.base_market_price, service.estimated_duration_minutes

    def setup_booking_specific_fields(
        self, booking: Booking, payload: CreateBookingRequest
    ) -> None:
        pass


class CustomBookingHandler(BaseBookingHandler):
    """Handler for custom service bookings created with user specifications."""

    async def build_service_snapshot_and_pricing(
        self, payload: CreateBookingRequest
    ) -> Tuple[ServiceSnapshot, float | None, int | None]:
        category_slug = payload.category_slug or "custom"
        category_name = category_slug.replace("-", " ").replace("_", " ").title()

        snapshot = ServiceSnapshot(
            service_id="custom",
            name=payload.custom_title or f"Custom {category_name} Work",
            category_id="custom",
            category_slug=category_slug,
            base_market_price=payload.custom_budget or 0.0,
            estimated_duration_minutes=60,
            is_inspection_required=False,
        )
        return snapshot, payload.custom_budget, 60

    def setup_booking_specific_fields(
        self, booking: Booking, payload: CreateBookingRequest
    ) -> None:
        booking.custom_title = payload.custom_title
        booking.custom_description = payload.custom_description
        booking.custom_budget = payload.custom_budget
        booking.category_slug = payload.category_slug


class InspectionBookingHandler(BaseBookingHandler):
    """Handler for site inspection request bookings."""

    async def build_service_snapshot_and_pricing(
        self, payload: CreateBookingRequest
    ) -> Tuple[ServiceSnapshot, float | None, int | None]:
        category_slug = payload.category_slug or "general"
        
        # If a service_id was provided optionally, try to resolve its category
        service_name = "Site Inspection & Diagnostics"
        if payload.service_id:
            try:
                s_oid = PydanticObjectId(payload.service_id)
                s = await Service.get(s_oid)
                if s:
                    category_slug = s.category_slug
                    service_name = f"Inspection: {s.name}"
            except Exception:
                pass
        else:
            category_title = category_slug.replace("-", " ").replace("_", " ").title()
            service_name = f"Inspection: {category_title}"

        snapshot = ServiceSnapshot(
            service_id="inspection",
            name=service_name,
            category_id="inspection",
            category_slug=category_slug,
            base_market_price=0.0,
            estimated_duration_minutes=30,
            is_inspection_required=True,
        )
        return snapshot, 0.0, 30

    def setup_booking_specific_fields(
        self, booking: Booking, payload: CreateBookingRequest
    ) -> None:
        booking.category_slug = payload.category_slug
        booking.inspection_status = InspectionStatus.PENDING
