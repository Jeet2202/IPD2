from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class InfrastructureError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

async def infrastructure_exception_handler(request: Request, exc: InfrastructureError):
    logger.error(f"Infrastructure Error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Infrastructure Error", "message": exc.message}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "details": exc.errors()}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected Error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred."}
    )

def register_exception_handlers(app):
    app.add_exception_handler(InfrastructureError, infrastructure_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
