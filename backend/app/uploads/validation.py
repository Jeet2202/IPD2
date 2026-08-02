"""
Image validation utility — enforces strict file size, extension, MIME type, and magic header checks.
"""

import os
from app.core.exceptions import BadRequestException

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB max size
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "application/octet-stream"}


def validate_profile_image(filename: str | None, content_type: str | None, file_bytes: bytes) -> str:
    """
    Validate image file against format, extension, size, and header magic bytes.

    Validation Order:
        1. File size (max 5 MB)
        2. Filename extension (.jpg, .jpeg, .png, .webp)
        3. Magic byte signature verification
        4. MIME type verification (supports image/* and application/octet-stream when magic bytes pass)

    Returns:
        Clean file extension string (e.g. '.jpg')

    Raises:
        BadRequestException if validation fails.
    """
    # 1. Check file content presence and size (5 MB limit)
    if not file_bytes or len(file_bytes) == 0:
        raise BadRequestException(
            message="Uploaded file is empty.",
            error_code="EMPTY_FILE_UPLOAD",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise BadRequestException(
            message=f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of 5.0 MB.",
            error_code="FILE_TOO_LARGE",
        )

    # 2. Check filename extension
    if not filename:
        raise BadRequestException(
            message="Filename is required for image upload.",
            error_code="MISSING_FILENAME",
        )

    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(
            message=f"Unsupported file type '{ext}'. Allowed types: .jpg, .jpeg, .png, .webp.",
            error_code="UNSUPPORTED_FILE_TYPE",
        )

    # 3. Verify Magic Header Bytes (prevention against extension spoofing)
    if file_bytes.startswith(b"\xFF\xD8\xFF"):  # JPEG magic bytes
        verified_ext = ".jpg"
    elif file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):  # PNG magic bytes
        verified_ext = ".png"
    elif file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]:  # WEBP magic bytes
        verified_ext = ".webp"
    else:
        raise BadRequestException(
            message="File content does not match valid JPEG, PNG, or WEBP image signatures.",
            error_code="INVALID_IMAGE_SIGNATURE",
        )

    # 4. Check Content-Type header if provided
    if content_type:
        clean_mime = content_type.split(";")[0].strip().lower()
        if clean_mime not in ALLOWED_MIME_TYPES:
            raise BadRequestException(
                message=f"Invalid MIME type '{content_type}'. Allowed types: image/jpeg, image/png, image/webp.",
                error_code="INVALID_MIME_TYPE",
            )

    return ext
