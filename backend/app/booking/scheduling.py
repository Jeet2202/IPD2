"""
Booking Scheduling & Time Slot Management Engine.

Configurable slot generator and validation rules.
Uses settings from app.core.config (single source of truth).
Prepared for future Worker Availability integration (Phase 4.5).
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import NamedTuple

from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.exceptions import BadRequestException


class TimeSlot(BaseModel):
    """Generated time slot DTO."""

    slot_id: str = Field(..., description="Unique slot label (HH:MM - HH:MM)", examples=["09:00 - 11:00"])
    start_time: str = Field(..., description="Start time in HH:MM format", examples=["09:00"])
    end_time: str = Field(..., description="End time in HH:MM format", examples=["11:00"])
    is_available: bool = Field(..., description="True if available for booking")
    reason: str | None = Field(default=None, description="Reason if slot is unavailable")


class AvailableSlotsResponse(BaseModel):
    """API response for GET /customer/bookings/slots."""

    date: str = Field(..., description="Requested date (YYYY-MM-DD)")
    is_date_available: bool = Field(..., description="True if date is within valid booking window")
    slots: list[TimeSlot] = Field(..., description="List of generated time slots")


def generate_time_slots_for_date(target_date: date) -> AvailableSlotsResponse:
    """
    Generate all time slots for a given date based on configurable settings.

    Business Rules:
        1. Past dates: returns is_date_available=False and empty slots list.
        2. Date exceeds max_advance_days: returns is_date_available=False and empty slots list.
        3. Slots generated from BOOKING_BUSINESS_START_HOUR to BOOKING_BUSINESS_END_HOUR.
        4. For today's date: slots where start_time < now + BOOKING_SAME_DAY_BUFFER_HOURS
           are marked is_available=False with reason "Slot time has passed".
        5. For future valid dates: all slots marked is_available=True.
    """
    today = date.today()
    max_date = today + timedelta(days=settings.BOOKING_MAX_ADVANCE_DAYS)

    if target_date < today or target_date > max_date:
        return AvailableSlotsResponse(
            date=target_date.isoformat(),
            is_date_available=False,
            slots=[],
        )

    slots: list[TimeSlot] = []

    # Generate slots from start hour to end hour
    current_minutes = settings.BOOKING_BUSINESS_START_HOUR * 60
    end_minutes = settings.BOOKING_BUSINESS_END_HOUR * 60
    duration = settings.BOOKING_SLOT_DURATION_MINUTES

    now_utc = datetime.now(timezone.utc)
    # Lead-time cutoff for same-day bookings
    cutoff_time = now_utc + timedelta(hours=settings.BOOKING_SAME_DAY_BUFFER_HOURS)

    while current_minutes + duration <= end_minutes:
        start_h, start_m = divmod(current_minutes, 60)
        end_h, end_m = divmod(current_minutes + duration, 60)

        start_str = f"{start_h:02d}:{start_m:02d}"
        end_str = f"{end_h:02d}:{end_m:02d}"
        slot_label = f"{start_str} - {end_str}"

        is_avail = True
        reason = None

        if target_date == today:
            # Check if this slot start time is already in the past or within buffer window
            # Convert slot start time to a datetime object for comparison (assuming local system time / naive)
            slot_dt = datetime.combine(today, time(hour=start_h, minute=start_m))
            now_local = datetime.now()
            cutoff_local = now_local + timedelta(hours=settings.BOOKING_SAME_DAY_BUFFER_HOURS)

            if slot_dt < cutoff_local:
                is_avail = False
                reason = "Slot time has passed or is too close"

        slots.append(
            TimeSlot(
                slot_id=slot_label,
                start_time=start_str,
                end_time=end_str,
                is_available=is_avail,
                reason=reason,
            )
        )

        current_minutes += duration

    return AvailableSlotsResponse(
        date=target_date.isoformat(),
        is_date_available=True,
        slots=slots,
    )


def validate_booking_schedule(
    scheduled_date: date | None,
    scheduled_time: str | None,
) -> None:
    """
    Validate that the requested date and time slot meet all scheduling rules.

    Raises:
        BadRequestException if validation fails.
    """
    if scheduled_date is None:
        return

    today = date.today()
    max_date = today + timedelta(days=settings.BOOKING_MAX_ADVANCE_DAYS)

    if scheduled_date < today:
        raise BadRequestException(
            message="Scheduled date cannot be in the past.",
            error_code="PAST_BOOKING_DATE",
        )

    if scheduled_date > max_date:
        raise BadRequestException(
            message=f"Scheduled date cannot exceed maximum advance booking window of {settings.BOOKING_MAX_ADVANCE_DAYS} days.",
            error_code="MAX_ADVANCE_WINDOW_EXCEEDED",
        )

    if scheduled_date == today and scheduled_time:
        # Check if the requested slot's start time on today has passed
        # Expecting scheduled_time like "09:00 - 11:00", "09:00 AM", or "09:00 AM - 11:00 AM"
        try:
            start_part = scheduled_time.split("-")[0].strip()
            upper_part = start_part.upper()
            is_pm = "PM" in upper_part
            is_am = "AM" in upper_part

            clean_part = "".join(c for c in start_part if c.isdigit() or c == ":").strip()
            parts = clean_part.split(":")
            if parts and parts[0]:
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 and parts[1] else 0

                if is_pm and hour < 12:
                    hour += 12
                elif is_am and hour == 12:
                    hour = 0

                slot_dt = datetime.combine(today, time(hour=hour, minute=minute))
                now_local = datetime.now()
                cutoff_local = now_local + timedelta(hours=settings.BOOKING_SAME_DAY_BUFFER_HOURS)

                if slot_dt < cutoff_local:
                    raise BadRequestException(
                        message="Selected time slot has already passed for today.",
                        error_code="PAST_TIME_SLOT",
                    )
        except BadRequestException:
            raise
        except Exception:
            # If custom format string, allow unless format fails parsing
            pass


# ---------------------------------------------------------------------------
# Time Overlap Utilities (used by scheduling conflict detection)
# ---------------------------------------------------------------------------

def parse_time_range_minutes(time_str: str) -> tuple[int, int] | None:
    """
    Parse a time range string into (start_minutes_since_midnight, end_minutes_since_midnight).

    Supported formats:
        "09:00 - 11:00"          → (540, 660)
        "09:00 AM - 11:00 AM"    → (540, 660)
        "02:00 PM - 04:00 PM"    → (840, 960)
        "09:00"                  → (540, 600)  single time → assume 60 min

    Returns None if the string cannot be parsed.
    """
    if not time_str:
        return None

    try:
        # Split on " - " to get start / end parts
        raw_parts = time_str.split(" - ", 1)
        start_part = raw_parts[0].strip()
        end_part = raw_parts[1].strip() if len(raw_parts) > 1 else None

        def _parse_part(part: str) -> int:
            """Return minutes since midnight for a single time string like '09:00' or '09:00 AM'."""
            upper = part.upper()
            is_pm = "PM" in upper
            is_am = "AM" in upper
            # Strip AM/PM and whitespace
            clean = "".join(c for c in part if c.isdigit() or c == ":").strip()
            segments = clean.split(":")
            hour = int(segments[0])
            minute = int(segments[1]) if len(segments) > 1 and segments[1] else 0
            if is_pm and hour < 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
            return hour * 60 + minute

        start_min = _parse_part(start_part)
        if end_part:
            end_min = _parse_part(end_part)
        else:
            end_min = start_min + 60  # default 60-minute duration

        # Sanity check: end must be after start
        if end_min <= start_min:
            return None

        return (start_min, end_min)

    except Exception:
        return None


def has_time_overlap(time_a: str, time_b: str) -> bool:
    """
    Return True if two time range strings have any temporal overlap.

    Two intervals [s1, e1) and [s2, e2) overlap iff s1 < e2 AND s2 < e1.
    Touching intervals (e.g. 09:00-10:00 and 10:00-12:00) are NOT considered overlapping.
    If either string fails to parse, returns False (safe/permissive default).

    Args:
        time_a: First time range string (e.g. "09:00 - 11:00")
        time_b: Second time range string (e.g. "10:00 - 12:00")

    Returns:
        True if the intervals overlap, False otherwise.

    Examples:
        has_time_overlap("09:00 - 11:00", "10:00 - 12:00") → True  (overlap 10:00-11:00)
        has_time_overlap("09:00 - 10:00", "10:00 - 12:00") → False (touching, not overlapping)
        has_time_overlap("09:00 - 11:00", "11:00 - 13:00") → False (touching, not overlapping)
        has_time_overlap("09:00 - 11:00", "09:30 - 10:30") → True  (fully nested)
    """
    range_a = parse_time_range_minutes(time_a)
    range_b = parse_time_range_minutes(time_b)

    if range_a is None or range_b is None:
        return False  # Safe default — can't determine overlap, don't block

    s1, e1 = range_a
    s2, e2 = range_b

    return s1 < e2 and s2 < e1


