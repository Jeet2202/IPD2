"""
Global exception handlers — registered on the FastAPI app.

Catches every exception type and serializes it into ErrorResponse:
    - AppException subclasses → controlled error with correct status code
    - HTTPException (from FastAPI/Starlette) → converted to ErrorResponse
    - RequestValidationError (Pydantic) → field-level validation errors
    - Unhandled exceptions → 500 with production-safe message

Design decisions:
    - Handlers are functions, not classes — FastAPI's add_exception_handler
      expects callables with (request, exc) signature.
    - Production: unhandled exceptions return generic "Internal server error".
      The real exception is logged with request_id for debugging.
    - Development (DEBUG=True): unhandled exceptions include the exception
      type and message in the response details for faster debugging.
    - Request ID is pulled from context vars and included in every response
      so frontend teams can reference it in support tickets.
"""

import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.context import request_id_var
from app.core.exceptions import AppException, ErrorResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Handler functions
# ---------------------------------------------------------------------------

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle all AppException subclasses (BadRequest, NotFound, etc.).

    These are intentional, controlled errors raised by feature modules.
    The error_code, message, and details are safe for client display.
    """
    logger.warning(
        "%s — %s: %s (details=%s)",
        exc.error_code,
        exc.status_code,
        exc.message,
        exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=request_id_var.get(),
        ).model_dump(),
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle FastAPI/Starlette HTTPException.

    Converts the bare HTTPException into our standard ErrorResponse format.
    This catches exceptions from FastAPI internals (e.g., 404 for unknown
    routes, 405 for wrong methods) and any manually raised HTTPException.
    """
    # Map common status codes to readable error codes
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
    }

    error_code = error_code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_code=error_code,
            message=message,
            request_id=request_id_var.get(),
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic request validation errors (422).

    Transforms Pydantic's raw error list into a cleaner format:
        [{"field": "body.email", "message": "value is not a valid email", "type": "value_error"}]

    This gives frontend teams field-level error mapping without
    exposing Pydantic internals (ctx, url, input).
    """
    details = []
    for error in exc.errors():
        # Build field path: "body.email" or "query.page"
        field_path = ".".join(str(loc) for loc in error.get("loc", []))
        details.append({
            "field": field_path,
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "unknown"),
        })

    logger.info(
        "Validation failed — %d field error(s): %s",
        len(details),
        [d["field"] for d in details],
    )

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Invalid request data",
            details=details,
            request_id=request_id_var.get(),
        ).model_dump(),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Catch-all for unhandled exceptions (500).

    Production: Returns a generic "Internal server error" message.
    The actual exception is logged with full traceback and request_id
    so developers can find it in logs without leaking internals.

    Development (DEBUG=True): Includes exception type and message
    in the response details for faster debugging without checking logs.
    """
    request_id = request_id_var.get()

    logger.exception(
        "Unhandled exception [request_id=%s] %s %s",
        request_id,
        request.method,
        request.url.path,
    )

    details = []
    if settings.DEBUG:
        details.append({
            "exception": type(exc).__name__,
            "message": str(exc),
        })

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            message="Internal server error",
            details=details,
            request_id=request_id,
        ).model_dump(),
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers on the FastAPI app.

    Called once from main.py after app creation. Order doesn't matter —
    FastAPI dispatches by exception type, not registration order.
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
