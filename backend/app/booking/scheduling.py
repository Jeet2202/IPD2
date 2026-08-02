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
        # Expecting scheduled_time like "09:00 - 11:00" or "09:00"
        try:
            start_part = scheduled_time.split("-")[0].strip()
            parts = start_part.split(":")
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0

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
