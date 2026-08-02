"""
Address Service — Business logic for customer address management.

Phase 4.3.3 Changes (GeoJSON Migration):
    - _to_response() extracts latitude/longitude from location.coordinates
      so the API response remains flat lat/lng (Flutter compatibility).
    - create_address() converts lat/lng payload to GeoJSONPoint.from_lat_lng().
    - update_address() converts lat/lng payload to GeoJSONPoint.from_lat_lng()
      when both are provided.
    - All other business rules are unchanged.

Business Rules enforced here (NOT in router, NOT in repository):
    1. Ownership: only the owning customer can access/modify their addresses.
    2. Default uniqueness: only one is_default=True per customer at any time.
    3. First address: automatically promoted to default.
    4. Deleting default: next-oldest address auto-promoted to default.
    5. Soft-delete only: is_deleted=True, never hard-delete.
    6. Requested default: clearing and re-setting via clear_default → save.

Future Booking Integration:
    - BookingService will call AddressService.get_address_for_booking(customer_id, address_id)
      to validate ownership and fetch a snapshot of the address at booking creation.
    - The snapshot (location, city, postal_code) is stored on the Booking document
      so address changes after booking don't affect the in-flight job.
"""

import logging

from beanie import PydanticObjectId

from app.address.models import Address, GeoJSONPoint
from app.address.repository import AddressRepository
from app.address.schemas import (
    AddressListResponse,
    AddressResponse,
    CreateAddressRequest,
    UpdateAddressRequest,
)
from app.core.exceptions import ForbiddenException, NotFoundException

logger = logging.getLogger(__name__)


def _to_response(address: Address) -> AddressResponse:
    """
    Convert an Address document to its response DTO.

    Extracts latitude and longitude from the GeoJSON location field
    (coordinates[1] and coordinates[0] respectively) so the API response
    continues to return flat lat/lng fields — Flutter is unaffected.
    """
    latitude: float | None = None
    longitude: float | None = None

    if address.location is not None:
        # GeoJSON coordinates: [longitude, latitude]
        longitude = address.location.coordinates[0]
        latitude = address.location.coordinates[1]

    return AddressResponse(
        id=str(address.id),
        customer_id=str(address.customer_id),
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
        latitude=latitude,
        longitude=longitude,
        is_default=address.is_default,
        is_deleted=address.is_deleted,
        created_at=address.created_at.isoformat(),
        updated_at=address.updated_at.isoformat(),
    )


def _verify_ownership(address: Address, customer_id: str) -> None:
    """
    Raise ForbiddenException if address does not belong to customer_id.
    Security guard — called before any read/write on a specific address.
    """
    if str(address.customer_id) != customer_id:
        raise ForbiddenException(
            message="You do not have permission to access this address.",
            error_code="ADDRESS_ACCESS_DENIED",
        )


def _build_location(latitude: float | None, longitude: float | None) -> GeoJSONPoint | None:
    """
    Convert flat lat/lng to a GeoJSONPoint, or return None if both are absent.

    GeoJSON stores [longitude, latitude] — always use this helper.
    """
    if latitude is not None and longitude is not None:
        return GeoJSONPoint.from_lat_lng(latitude=latitude, longitude=longitude)
    return None


class AddressService:
    """Business logic handler for all customer address operations."""

    # ── List ─────────────────────────────────────────────────────────────────

    @classmethod
    async def list_addresses(cls, customer_id: str) -> AddressListResponse:
        """Return all non-deleted addresses for the authenticated customer."""
        addresses = await AddressRepository.list_by_customer(customer_id)
        dtos = [_to_response(a) for a in addresses]
        return AddressListResponse(total=len(dtos), addresses=dtos)

    # ── Get Single ───────────────────────────────────────────────────────────

    @classmethod
    async def get_address(cls, customer_id: str, address_id: str) -> AddressResponse:
        """
        Fetch a single address by ID.

        Raises:
            NotFoundException: address not found or soft-deleted.
            ForbiddenException: address belongs to a different customer.
        """
        address = await AddressRepository.get_by_id(address_id)
        if not address or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        _verify_ownership(address, customer_id)
        return _to_response(address)

    # ── Create ───────────────────────────────────────────────────────────────

    @classmethod
    async def create_address(
        cls, customer_id: str, payload: CreateAddressRequest
    ) -> AddressResponse:
        """
        Create a new address for the authenticated customer.

        Business rules:
            - If this is the customer's first address → is_default=True automatically.
            - If payload.is_default=True → clear existing default first.
            - latitude/longitude from payload are converted to GeoJSON Point (location field).
        """
        cid = PydanticObjectId(customer_id)

        # Determine is_default
        active_count = await AddressRepository.count_active(cid)
        make_default = payload.is_default or (active_count == 0)

        if make_default:
            await AddressRepository.clear_default_for_customer(cid)

        address = Address(
            customer_id=cid,
            label=payload.label,
            full_name=payload.full_name,
            phone=payload.phone,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            landmark=payload.landmark,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            postal_code=payload.postal_code,
            location=_build_location(payload.latitude, payload.longitude),
            is_default=make_default,
        )

        address = await AddressRepository.create(address)
        logger.info(
            "Address created: id=%s customer_id=%s is_default=%s has_location=%s",
            address.id, customer_id, make_default, address.location is not None,
        )
        return _to_response(address)

    # ── Update ────────────────────────────────────────────────────────────────

    @classmethod
    async def update_address(
        cls, customer_id: str, address_id: str, payload: UpdateAddressRequest
    ) -> AddressResponse:
        """
        Update an existing address.

        Ownership is verified before any mutation.
        Raises NotFoundException if address not found or deleted.
        latitude/longitude, if provided, are converted to GeoJSON Point.
        """
        address = await AddressRepository.get_by_id(address_id)
        if not address or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        _verify_ownership(address, customer_id)

        # Apply partial updates
        if payload.label is not None:
            address.label = payload.label
        if payload.full_name is not None:
            address.full_name = payload.full_name
        if payload.phone is not None:
            address.phone = payload.phone
        if payload.address_line_1 is not None:
            address.address_line_1 = payload.address_line_1
        if payload.address_line_2 is not None:
            address.address_line_2 = payload.address_line_2
        if payload.landmark is not None:
            address.landmark = payload.landmark
        if payload.city is not None:
            address.city = payload.city
        if payload.state is not None:
            address.state = payload.state
        if payload.country is not None:
            address.country = payload.country
        if payload.postal_code is not None:
            address.postal_code = payload.postal_code

        # Update GeoJSON location when both lat and lng are provided
        new_location = _build_location(payload.latitude, payload.longitude)
        if new_location is not None:
            address.location = new_location

        await AddressRepository.save(address)
        logger.info("Address updated: id=%s customer_id=%s", address_id, customer_id)
        return _to_response(address)

    # ── Delete (Soft) ─────────────────────────────────────────────────────────

    @classmethod
    async def delete_address(cls, customer_id: str, address_id: str) -> dict:
        """
        Soft-delete an address by setting is_deleted=True.

        Business rules:
            - If deleted address was the default → auto-promote oldest remaining address.
            - Never hard-delete.
        """
        address = await AddressRepository.get_by_id(address_id)
        if not address or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        _verify_ownership(address, customer_id)

        was_default = address.is_default
        await AddressRepository.soft_delete(address)

        # Auto-promote next oldest address if deleted address was default
        if was_default:
            next_address = await AddressRepository.get_oldest_active(
                customer_id, exclude_id=address_id
            )
            if next_address:
                next_address.is_default = True
                await AddressRepository.save(next_address)
                logger.info(
                    "Auto-promoted address id=%s as new default for customer_id=%s",
                    next_address.id, customer_id,
                )

        logger.info("Address soft-deleted: id=%s customer_id=%s", address_id, customer_id)
        return {"message": "Address deleted successfully."}

    # ── Set Default ────────────────────────────────────────────────────────────

    @classmethod
    async def set_default_address(
        cls, customer_id: str, address_id: str
    ) -> AddressResponse:
        """
        Designate an address as the customer's default.

        Business rules:
            - All existing defaults for this customer are cleared first.
            - Then the target address is set as default.
            - Ownership verification happens before any mutation.
        """
        address = await AddressRepository.get_by_id(address_id)
        if not address or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        _verify_ownership(address, customer_id)

        if address.is_default:
            # Already the default — idempotent response
            return _to_response(address)

        # Clear all existing defaults
        await AddressRepository.clear_default_for_customer(customer_id)

        # Set this address as default
        address.is_default = True
        await AddressRepository.save(address)
        logger.info(
            "Default address set: id=%s customer_id=%s", address_id, customer_id
        )
        return _to_response(address)

    # ── Booking Integration Helper ─────────────────────────────────────────────

    @classmethod
    async def get_address_for_booking(
        cls, customer_id: str, address_id: str
    ) -> Address:
        """
        Validate ownership and return the raw Address document for booking creation.

        Called by BookingService (Phase 4.4). Returns the model directly so
        BookingService can snapshot location (GeoJSON Point) / city / postal_code
        into the Booking document. The booking stores the GeoJSON Point so that
        $geoNear aggregation can calculate distance from worker to job site.

        Raises:
            NotFoundException: address not found or soft-deleted.
            ForbiddenException: address belongs to a different customer.
        """
        address = await AddressRepository.get_by_id(address_id)
        if not address or address.is_deleted:
            raise NotFoundException(
                message="Address not found.",
                error_code="ADDRESS_NOT_FOUND",
            )
        _verify_ownership(address, customer_id)
        return address
