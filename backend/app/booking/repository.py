"""
Booking Repository — pure database access layer for the bookings collection.

Rules:
    - ONLY database queries here — no business logic.
    - Booking number generation uses an atomic MongoDB counter sequence to
      guarantee uniqueness under concurrent requests (no race conditions).
    - The repository is ownership-agnostic: service layer enforces ownership.

Booking number format: KS{YEAR}{5-digit-sequence}
    Examples: KS202600001, KS202600042, KS202710000
    Sequence resets per year (tracked in the 'sequences' collection).
"""

import logging
from datetime import datetime, timezone

from beanie import PydanticObjectId
from pymongo import ReturnDocument

from app.booking.models import Booking
from app.database import get_database

logger = logging.getLogger(__name__)

# Collection name for atomic sequence counters
_SEQUENCES_COLLECTION = "sequences"


async def _next_booking_number() -> str:
    """
    Generate the next unique booking number atomically.

    Uses MongoDB findOneAndUpdate with upsert to atomically increment
    a per-year counter. Thread-safe and race-condition-free.

    Format: KS{YEAR}{SEQ:05d}
        KS202600001 — first booking of 2026
        KS202700001 — first booking of 2027 (counter resets)
    """
    year = datetime.now(timezone.utc).year
    seq_key = f"booking_seq_{year}"

    db = get_database()
    sequences = db[_SEQUENCES_COLLECTION]

    doc = await sequences.find_one_and_update(
        {"_id": seq_key},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )

    seq: int = doc["seq"]
    booking_number = f"KS{year}{seq:05d}"
    logger.debug("Generated booking_number=%s", booking_number)
    return booking_number


class BookingRepository:
    """Encapsulates all Beanie queries for the bookings collection."""

    # ── Create ───────────────────────────────────────────────────────────────

    @staticmethod
    async def create(booking: Booking) -> Booking:
        """Persist a new Booking document and return it."""
        await booking.insert()
        logger.info(
            "Created booking id=%s number=%s customer_id=%s",
            booking.id,
            booking.booking_number,
            booking.customer_id,
        )
        return booking

    @staticmethod
    async def generate_booking_number() -> str:
        """Return the next unique booking number (KS{YEAR}{SEQ:05d})."""
        return await _next_booking_number()

    # ── Read ─────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_by_id(booking_id: str | PydanticObjectId) -> Booking | None:
        """
        Fetch a single booking by its ObjectId.

        Returns the document regardless of status.
        The service layer checks ownership.
        """
        try:
            oid = (
                PydanticObjectId(str(booking_id))
                if isinstance(booking_id, str)
                else booking_id
            )
            return await Booking.get(oid)
        except Exception:
            return None

    @staticmethod
    async def get_by_number(booking_number: str) -> Booking | None:
        """Fetch a booking by its human-readable booking number."""
        return await Booking.find_one(Booking.booking_number == booking_number)

    @staticmethod
    async def list_by_customer(
        customer_id: str | PydanticObjectId,
        *,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Booking]:
        """
        Return bookings for a customer, newest first.

        Args:
            customer_id: Customer's User ObjectId.
            status:      Optional status filter (e.g., "pending").
            skip:        Pagination offset.
            limit:       Maximum results (capped by caller).
        """
        cid = (
            PydanticObjectId(str(customer_id))
            if isinstance(customer_id, str)
            else customer_id
        )
        query = Booking.find(Booking.customer_id == cid)
        if status:
            query = query.find({"status": status})
        return (
            await query
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_by_customer(
        customer_id: str | PydanticObjectId,
        *,
        status: str | None = None,
    ) -> int:
        """Count bookings for a customer, optionally filtered by status."""
        cid = (
            PydanticObjectId(str(customer_id))
            if isinstance(customer_id, str)
            else customer_id
        )
        query = Booking.find(Booking.customer_id == cid)
        if status:
            query = query.find({"status": status})
        return await query.count()

    # ── Update ────────────────────────────────────────────────────────────────

    @staticmethod
    async def list_by_worker(
        worker_id: str | PydanticObjectId,
        *,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Booking]:
        """
        Return bookings assigned to a worker, newest first.

        Args:
            worker_id: Worker's User ObjectId.
            status:    Optional status filter (e.g., 'assigned').
            skip:      Pagination offset.
            limit:     Maximum results.
        """
        wid = (
            PydanticObjectId(str(worker_id))
            if isinstance(worker_id, str)
            else worker_id
        )
        query = Booking.find(Booking.worker_id == wid)
        if status:
            query = query.find({"status": status})
        return (
            await query
            .sort("-created_at")
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_by_worker(
        worker_id: str | PydanticObjectId,
        *,
        status: str | None = None,
    ) -> int:
        """Count bookings assigned to a worker, optionally filtered by status."""
        wid = (
            PydanticObjectId(str(worker_id))
            if isinstance(worker_id, str)
            else worker_id
        )
        query = Booking.find(Booking.worker_id == wid)
        if status:
            query = query.find({"status": status})
        return await query.count()

    @staticmethod
    async def save(booking: Booking) -> Booking:
        """Persist changes to an existing booking document."""
        await booking.save()
        return booking
