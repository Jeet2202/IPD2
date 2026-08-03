"""
Quotation Repository — database access layer for the quotations collection.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from beanie import PydanticObjectId
from pymongo import ReturnDocument

from app.database import get_database
from app.quotation.models import Quotation
from app.utils.enums import QuotationStatus

logger = logging.getLogger(__name__)

_SEQUENCES_COLLECTION = "sequences"


async def _next_quotation_number() -> str:
    """
    Generate the next unique quotation number atomically.

    Format: QT{YEAR}{SEQ:05d}
        QT202600001 — first quotation of 2026
        QT202600002 — second quotation of 2026
    """
    year = datetime.now(timezone.utc).year
    seq_key = f"quotation_seq_{year}"

    db = get_database()
    sequences = db[_SEQUENCES_COLLECTION]

    doc = await sequences.find_one_and_update(
        {"_id": seq_key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    seq: int = doc["seq"]
    quotation_number = f"QT{year}{seq:05d}"
    logger.debug("Generated quotation_number=%s", quotation_number)
    return quotation_number


class QuotationRepository:
    """Encapsulates Beanie MongoDB operations for the quotations collection."""

    @staticmethod
    async def generate_quotation_number() -> str:
        """Expose quotation number generator."""
        return await _next_quotation_number()

    @staticmethod
    async def create_quotation(quotation: Quotation) -> Quotation:
        """Insert a new quotation document into MongoDB."""
        return await quotation.insert()

    @staticmethod
    async def get_quotation_by_id(
        quotation_id: str | PydanticObjectId,
    ) -> Quotation | None:
        """Find a quotation by ID."""
        if isinstance(quotation_id, str):
            if not PydanticObjectId.is_valid(quotation_id):
                return None
            quotation_id = PydanticObjectId(quotation_id)
        return await Quotation.get(quotation_id)

    @staticmethod
    async def get_quotation_by_number(quotation_number: str) -> Quotation | None:
        """Find a quotation by unique quotation_number."""
        return await Quotation.find_one({"quotation_number": quotation_number})

    @staticmethod
    async def list_quotations_by_booking(
        booking_id: PydanticObjectId,
        status: QuotationStatus | None = None,
    ) -> list[Quotation]:
        """List all quotations submitted for a specific booking."""
        filters: dict[str, Any] = {"booking_id": booking_id}
        if status:
            filters["quotation_status"] = status.value
        return await Quotation.find(filters).sort("-created_at").to_list()

    @staticmethod
    async def list_quotations_by_worker(
        worker_id: PydanticObjectId,
        status: QuotationStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Quotation], int]:
        """List quotations submitted by a specific worker."""
        filters: dict[str, Any] = {"worker_id": worker_id}
        if status:
            filters["quotation_status"] = status.value

        query = Quotation.find(filters)
        total = await query.count()
        items = await query.sort("-created_at").skip(skip).limit(limit).to_list()
        return items, total

    @staticmethod
    async def update_quotation(quotation: Quotation) -> Quotation:
        """Save changes to an existing quotation document."""
        return await quotation.save()
