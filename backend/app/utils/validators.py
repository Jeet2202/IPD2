"""
Reusable Pydantic validators — Annotated types with built-in validation.

Uses PEP 593 Annotated types so feature modules get validated fields
by type annotation alone — no manual validator decorators needed.

Usage in Pydantic models:
    from app.utils.validators import PhoneNumber, ObjectIdStr, NameStr

    class CreateWorkerSchema(BaseModel):
        phone: PhoneNumber          # Validated Indian phone number
        name: NameStr               # 2-100 chars, stripped
        referral_id: ObjectIdStr    # Valid MongoDB ObjectId

These types work with FastAPI path/query params too:
    @router.get("/workers/{worker_id}")
    async def get_worker(worker_id: ObjectIdStr): ...
"""

from typing import Annotated

from pydantic import AfterValidator, Field, StringConstraints

from app.utils.constants import (
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    MIN_NAME_LENGTH,
    OBJECT_ID_REGEX,
    PHONE_REGEX,
    PIN_CODE_REGEX,
)


# ---------------------------------------------------------------------------
# Validator Functions
# ---------------------------------------------------------------------------

def validate_phone_number(value: str) -> str:
    """
    Validate Indian phone number format: +91XXXXXXXXXX.

    Strips whitespace and validates against the pattern.
    Returns the normalized phone number.
    """
    value = value.strip().replace(" ", "").replace("-", "")
    if not PHONE_REGEX.match(value):
        raise ValueError(
            "Invalid phone number. Expected format: +91XXXXXXXXXX "
            "(10 digits starting with 6-9)"
        )
    return value


def validate_object_id(value: str) -> str:
    """
    Validate MongoDB ObjectId format: 24 hex characters.

    Used for path parameters and foreign key references.
    """
    value = value.strip()
    if not OBJECT_ID_REGEX.match(value):
        raise ValueError(
            "Invalid ID format. Expected 24-character hex string"
        )
    return value


def validate_pin_code(value: str) -> str:
    """Validate Indian PIN code: exactly 6 digits."""
    value = value.strip()
    if not PIN_CODE_REGEX.match(value):
        raise ValueError("Invalid PIN code. Expected exactly 6 digits")
    return value


def validate_non_empty_string(value: str) -> str:
    """Reject empty or whitespace-only strings."""
    value = value.strip()
    if not value:
        raise ValueError("Value cannot be empty")
    return value


# ---------------------------------------------------------------------------
# Annotated Types — use these as field types in Pydantic models
# ---------------------------------------------------------------------------

# Phone number: +91XXXXXXXXXX, auto-stripped and validated
PhoneNumber = Annotated[
    str,
    AfterValidator(validate_phone_number),
    Field(
        description="Indian phone number in +91XXXXXXXXXX format",
        examples=["+919876543210"],
    ),
]

# MongoDB ObjectId: 24-char hex string
ObjectIdStr = Annotated[
    str,
    AfterValidator(validate_object_id),
    Field(
        description="MongoDB ObjectId (24-char hex)",
        examples=["507f1f77bcf86cd799439011"],
    ),
]

# Name field: 2-100 chars, stripped, no leading/trailing whitespace
NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
    ),
]

# Description field: up to 2000 chars, stripped
DescriptionStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=MAX_DESCRIPTION_LENGTH,
    ),
]

# Non-empty string: stripped, must have at least 1 char
NonEmptyStr = Annotated[
    str,
    AfterValidator(validate_non_empty_string),
]

# PIN code: exactly 6 digits (Indian postal code)
PinCode = Annotated[
    str,
    AfterValidator(validate_pin_code),
    Field(
        description="Indian PIN code (6 digits)",
        examples=["400001"],
    ),
]
