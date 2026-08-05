"""
Unit tests for Booking types (STANDARD, CUSTOM_SERVICE, INSPECTION_REQUEST) and inspection workflow.
"""

import pytest
from app.utils.enums import BookingType, InspectionStatus
from app.booking.schemas import CreateBookingRequest


def test_create_booking_request_validation():
    # 1. Standard booking requires service_id
    with pytest.raises(ValueError, match="service_id is required"):
        CreateBookingRequest(
            address_id="60d5ec49f1a2c8b1f8e4e1b2",
            booking_type=BookingType.NORMAL_SERVICE,
        )

    # 2. Custom service requires custom_title and category_slug
    with pytest.raises(ValueError, match="custom_title is required"):
        CreateBookingRequest(
            address_id="60d5ec49f1a2c8b1f8e4e1b2",
            booking_type=BookingType.CUSTOM_SERVICE,
            category_slug="plumbing",
        )

    # 3. Custom service valid payload
    req = CreateBookingRequest(
        address_id="60d5ec49f1a2c8b1f8e4e1b2",
        booking_type=BookingType.CUSTOM_SERVICE,
        custom_title="Custom Pipe Fitting",
        category_slug="plumbing",
        custom_budget=1500.0,
    )
    assert req.custom_title == "Custom Pipe Fitting"
    assert req.booking_type == BookingType.CUSTOM_SERVICE

    # 4. Inspection request requires problem_description
    with pytest.raises(ValueError, match="Problem description is required"):
        CreateBookingRequest(
            address_id="60d5ec49f1a2c8b1f8e4e1b2",
            booking_type=BookingType.INSPECTION_REQUEST,
            category_slug="plumbing",
        )

    # 5. Inspection request valid payload
    insp = CreateBookingRequest(
        address_id="60d5ec49f1a2c8b1f8e4e1b2",
        booking_type=BookingType.INSPECTION_REQUEST,
        category_slug="plumbing",
        problem_description="Leaking main valve under kitchen sink",
    )
    assert insp.problem_description == "Leaking main valve under kitchen sink"
    assert insp.booking_type == BookingType.INSPECTION_REQUEST
