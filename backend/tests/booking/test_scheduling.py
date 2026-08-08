"""
Unit tests for Booking Scheduling engine and time slot validation.
"""

from datetime import date, datetime, timedelta
import pytest

from app.booking.scheduling import generate_time_slots_for_date, validate_booking_schedule
from app.core.exceptions import BadRequestException


def test_generate_time_slots_past_date():
    yesterday = date.today() - timedelta(days=1)
    res = generate_time_slots_for_date(yesterday)
    assert res.is_date_available is False
    assert len(res.slots) == 0


def test_generate_time_slots_future_date():
    tomorrow = date.today() + timedelta(days=1)
    res = generate_time_slots_for_date(tomorrow)
    assert res.is_date_available is True
    assert len(res.slots) > 0
    assert all(s.is_available for s in res.slots)


def test_validate_booking_schedule_past_date():
    yesterday = date.today() - timedelta(days=1)
    with pytest.raises(BadRequestException) as exc_info:
        validate_booking_schedule(yesterday, "10:00 AM")
    assert exc_info.value.error_code == "PAST_BOOKING_DATE"


def test_validate_booking_schedule_past_slot_today():
    today = date.today()
    # 01:00 AM on today has already passed
    with pytest.raises(BadRequestException) as exc_info:
        validate_booking_schedule(today, "01:00 AM")
    assert exc_info.value.error_code == "PAST_TIME_SLOT"


def test_validate_booking_schedule_future_slot_today():
    today = date.today()
    future_hour = (datetime.now().hour + 3) % 24
    if future_hour > datetime.now().hour:
        slot_str = f"{future_hour:02d}:00"
        # Should not raise exception
        validate_booking_schedule(today, slot_str)
