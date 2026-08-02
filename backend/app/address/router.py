"""
Address API Router — Customer address CRUD endpoints.

All endpoints:
    - Require authenticated customer role (CustomerDep).
    - Follow Router → Service → Repository → Model pattern.
    - No business logic in this file.

Endpoints:
    GET    /customer/addresses              List all addresses
    GET    /customer/addresses/{id}         Get single address
    POST   /customer/addresses              Create address
    PUT    /customer/addresses/{id}         Update address
    DELETE /customer/addresses/{id}         Soft-delete address
    PATCH  /customer/addresses/{id}/default Set as default
"""

import logging

from fastapi import APIRouter, status

from app.address.schemas import (
    AddressListResponse,
    AddressResponse,
    CreateAddressRequest,
    UpdateAddressRequest,
)
from app.address.service import AddressService
from app.core.dependencies import CustomerDep

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /addresses — List all customer addresses
# ---------------------------------------------------------------------------

@router.get(
    "/addresses",
    response_model=AddressListResponse,
    status_code=status.HTTP_200_OK,
    summary="List customer addresses",
    description=(
        "Retrieve all saved, non-deleted addresses for the authenticated customer. "
        "Default address appears first. Requires customer role."
    ),
)
async def list_addresses(
    current_user: CustomerDep,
) -> AddressListResponse:
    """List all active addresses for the current customer."""
    return await AddressService.list_addresses(current_user.id)


# ---------------------------------------------------------------------------
# GET /addresses/{address_id} — Get single address
# ---------------------------------------------------------------------------

@router.get(
    "/addresses/{address_id}",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific address",
    description=(
        "Fetch a single customer address by ID. "
        "Returns 404 if not found or soft-deleted. "
        "Returns 403 if the address belongs to a different customer."
    ),
)
async def get_address(
    address_id: str,
    current_user: CustomerDep,
) -> AddressResponse:
    """Get a single address by ID for the current customer."""
    return await AddressService.get_address(current_user.id, address_id)


# ---------------------------------------------------------------------------
# POST /addresses — Create a new address
# ---------------------------------------------------------------------------

@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
    description=(
        "Add a new delivery/service address for the authenticated customer. "
        "The first address is automatically set as default. "
        "Set is_default=true to override the existing default."
    ),
)
async def create_address(
    payload: CreateAddressRequest,
    current_user: CustomerDep,
) -> AddressResponse:
    """Create a new address for the current customer."""
    return await AddressService.create_address(current_user.id, payload)


# ---------------------------------------------------------------------------
# PUT /addresses/{address_id} — Update an address
# ---------------------------------------------------------------------------

@router.put(
    "/addresses/{address_id}",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing address",
    description=(
        "Update one or more fields of an existing address. "
        "Only fields explicitly provided in the request body are updated. "
        "Returns 404 if not found and 403 if not owned by the current customer."
    ),
)
async def update_address(
    address_id: str,
    payload: UpdateAddressRequest,
    current_user: CustomerDep,
) -> AddressResponse:
    """Update an address belonging to the current customer."""
    return await AddressService.update_address(current_user.id, address_id, payload)


# ---------------------------------------------------------------------------
# DELETE /addresses/{address_id} — Soft-delete an address
# ---------------------------------------------------------------------------

@router.delete(
    "/addresses/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a customer address",
    description=(
        "Soft-delete an address (is_deleted=True). The document is never permanently removed. "
        "If the deleted address was the default, the next oldest address is auto-promoted to default. "
        "Returns 404 if not found and 403 if not owned by the current customer."
    ),
)
async def delete_address(
    address_id: str,
    current_user: CustomerDep,
) -> dict:
    """Soft-delete an address belonging to the current customer."""
    return await AddressService.delete_address(current_user.id, address_id)


# ---------------------------------------------------------------------------
# PATCH /addresses/{address_id}/default — Set default address
# ---------------------------------------------------------------------------

@router.patch(
    "/addresses/{address_id}/default",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Set an address as default",
    description=(
        "Mark the specified address as the customer's default address for bookings. "
        "All other addresses for this customer will have their default flag cleared. "
        "Idempotent — calling this on the already-default address returns 200 without changes."
    ),
)
async def set_default_address(
    address_id: str,
    current_user: CustomerDep,
) -> AddressResponse:
    """Set the specified address as the default for the current customer."""
    return await AddressService.set_default_address(current_user.id, address_id)
