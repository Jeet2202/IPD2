"""
General-purpose helper functions — used across all feature modules.

Pure utility functions with no business logic, no side effects, and
no external dependencies (except stdlib). Each function does one thing.

These are the kind of functions every feature module ends up needing.
Centralizing them here prevents 10 different slugify() implementations.
"""

import re
import uuid
from typing import Any


# ---------------------------------------------------------------------------
# ID Generation
# ---------------------------------------------------------------------------

def generate_short_id(prefix: str = "", length: int = 12) -> str:
    """
    Generate a short unique ID from UUID4.

    Shorter than a full UUID but still collision-resistant for
    application-level identifiers (request IDs, reference numbers).

    Args:
        prefix: Optional prefix (e.g., 'job_', 'inv_').
        length: Number of hex characters (default 12).

    Returns:
        String like 'job_a1b2c3d4e5f6' or 'a1b2c3d4e5f6'.
    """
    short = uuid.uuid4().hex[:length]
    return f"{prefix}{short}" if prefix else short


def generate_reference_number(prefix: str = "REF") -> str:
    """
    Generate a human-readable reference number.

    Format: PREFIX-XXXXXXXX (uppercase, 8 chars).
    Used for job IDs, booking references, and invoice numbers
    that customers see in SMS/notifications.

    Args:
        prefix: Reference type prefix (e.g., 'JOB', 'INV', 'PAY').

    Returns:
        String like 'JOB-A1B2C3D4'.
    """
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# String Utilities
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.

    Lowercase, spaces to hyphens, strips non-alphanumeric characters,
    collapses multiple hyphens.

    Args:
        text: Input text (e.g., 'AC Technician (Expert)').

    Returns:
        Slug string (e.g., 'ac-technician-expert').
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)     # Remove non-word chars
    text = re.sub(r"[\s_]+", "-", text)       # Spaces/underscores to hyphens
    text = re.sub(r"-+", "-", text)           # Collapse multiple hyphens
    return text.strip("-")


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max_length, adding suffix if truncated.

    Won't cut in the middle of a word — breaks at the last space.

    Args:
        text: Input text.
        max_length: Maximum output length (including suffix).
        suffix: String to append if truncated.

    Returns:
        Truncated string or original if within limit.
    """
    if len(text) <= max_length:
        return text

    truncated = text[: max_length - len(suffix)]
    # Don't cut mid-word — find the last space
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix


# ---------------------------------------------------------------------------
# Phone & Sensitive Data
# ---------------------------------------------------------------------------

def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number by removing spaces, dashes, and parentheses.

    Does NOT validate — use PhoneNumber validator type for that.

    Args:
        phone: Raw phone input (e.g., '+91 98765 43210').

    Returns:
        Cleaned phone (e.g., '+919876543210').
    """
    return re.sub(r"[\s\-\(\)]+", "", phone)


def mask_phone(phone: str) -> str:
    """
    Mask a phone number for display/logging.

    Shows only last 4 digits: '+91******3210'

    Args:
        phone: Full phone number.

    Returns:
        Masked phone number.
    """
    if len(phone) <= 4:
        return "****"
    return phone[:-4].replace(phone[:-4], "*" * len(phone[:-4])) + phone[-4:]


def mask_email(email: str) -> str:
    """
    Mask an email address for display/logging.

    Shows first 2 chars and domain: 'jo***@gmail.com'

    Args:
        email: Full email address.

    Returns:
        Masked email address.
    """
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[:2] + "***"
    return f"{masked_local}@{domain}"


# ---------------------------------------------------------------------------
# Data Utilities
# ---------------------------------------------------------------------------

def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """
    Remove keys with None values from a dictionary.

    Used when building MongoDB update queries — $set should not
    include fields the client didn't send.

    Args:
        data: Input dictionary.

    Returns:
        New dictionary with None values removed.
    """
    return {k: v for k, v in data.items() if v is not None}


def flatten_dict(
    data: dict[str, Any],
    parent_key: str = "",
    sep: str = ".",
) -> dict[str, Any]:
    """
    Flatten a nested dictionary with dot-notation keys.

    Used for MongoDB $set operations on nested documents:
        flatten_dict({"address": {"city": "Mumbai"}})
        -> {"address.city": "Mumbai"}

    Args:
        data: Nested dictionary.
        parent_key: Prefix for keys (used in recursion).
        sep: Separator between key levels.

    Returns:
        Flat dictionary with dot-notation keys.
    """
    items: list[tuple[str, Any]] = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    return dict(items)
