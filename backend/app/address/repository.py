"""
Address Repository — pure database access layer for customer_addresses collection.

Rules:
    - ONLY database queries here — no business logic.
    - All soft-deleted documents (is_deleted=True) are excluded from queries
      unless explicitly requested.
    - Ownership verification (customer_id check) is done at the SERVICE layer,
      not here. The repository is intentionally unopinionated about ownership.
"""

import logging

from beanie import PydanticObjectId

from app.address.models import Address

logger = logging.getLogger(__name__)


class AddressRepository:
    """Encapsulates Beanie queries for the customer_addresses collection."""

    # ── Create ───────────────────────────────────────────────────────────────

    @staticmethod
    async def create(address: Address) -> Address:
        """Persist a new Address document and return it."""
        await address.insert()
        logger.info(
            "Created address id=%s for customer_id=%s",
            address.id,
            address.customer_id,
        )
        return address

    # ── Read ─────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_by_id(address_id: str | PydanticObjectId) -> Address | None:
        """
        Fetch a single address by its ObjectId.

        Returns the document regardless of is_deleted status.
        The service layer checks ownership and deletion state.
        """
        oid = PydanticObjectId(str(address_id)) if isinstance(address_id, str) else address_id
        return await Address.get(oid)

    @staticmethod
    async def list_by_customer(
        customer_id: str | PydanticObjectId,
    ) -> list[Address]:
        """
        Return all non-deleted addresses for a customer, default address first.
        """
        cid = PydanticObjectId(str(customer_id)) if isinstance(customer_id, str) else customer_id
        return (
            await Address.find(
                Address.customer_id == cid,
                Address.is_deleted == False,  # noqa: E712
            )
            .sort("-is_default", "+created_at")
            .to_list()
        )

    @staticmethod
    async def get_default(
        customer_id: str | PydanticObjectId,
    ) -> Address | None:
        """Fetch the current default (non-deleted) address for a customer."""
        cid = PydanticObjectId(str(customer_id)) if isinstance(customer_id, str) else customer_id
        return await Address.find_one(
            Address.customer_id == cid,
            Address.is_default == True,  # noqa: E712
            Address.is_deleted == False,  # noqa: E712
        )

    @staticmethod
    async def count_active(customer_id: str | PydanticObjectId) -> int:
        """Return the count of non-deleted addresses for a customer."""
        cid = PydanticObjectId(str(customer_id)) if isinstance(customer_id, str) else customer_id
        return await Address.find(
            Address.customer_id == cid,
            Address.is_deleted == False,  # noqa: E712
        ).count()

    @staticmethod
    async def get_oldest_active(
        customer_id: str | PydanticObjectId,
        exclude_id: str | PydanticObjectId | None = None,
    ) -> Address | None:
        """
        Fetch the oldest (by created_at) non-deleted, non-default address for a customer.

        Used when the default is deleted and we need to auto-promote another address.
        """
        cid = PydanticObjectId(str(customer_id)) if isinstance(customer_id, str) else customer_id
        query = Address.find(
            Address.customer_id == cid,
            Address.is_deleted == False,  # noqa: E712
        )
        if exclude_id is not None:
            eid = PydanticObjectId(str(exclude_id)) if isinstance(exclude_id, str) else exclude_id
            query = query.find({"_id": {"$ne": eid}})
        return await query.sort("+created_at").first_or_none()

    # ── Update ────────────────────────────────────────────────────────────────

    @staticmethod
    async def save(address: Address) -> Address:
        """Persist changes to an existing address document."""
        await address.save()
        return address

    @staticmethod
    async def clear_default_for_customer(
        customer_id: str | PydanticObjectId,
    ) -> None:
        """
        Set is_default=False on ALL non-deleted addresses for a customer.

        Called before setting a new default to guarantee uniqueness.
        """
        cid = PydanticObjectId(str(customer_id)) if isinstance(customer_id, str) else customer_id
        await Address.find(
            Address.customer_id == cid,
            Address.is_deleted == False,  # noqa: E712
            Address.is_default == True,  # noqa: E712
        ).update_many({"$set": {"is_default": False}})
        logger.debug("Cleared default flag for customer_id=%s", cid)

    # ── Soft Delete ───────────────────────────────────────────────────────────

    @staticmethod
    async def soft_delete(address: Address) -> Address:
        """Mark address as deleted (is_deleted=True) without removing the document."""
        address.is_deleted = True
        address.is_default = False
        await address.save()
        logger.info("Soft-deleted address id=%s", address.id)
        return address
