import time
import uuid
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Log incoming request
        logger.info(f"Incoming Request - ID: {request_id} - Method: {request.method} - URL: {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log outgoing response
            logger.info(
                f"Outgoing Response - ID: {request_id} - Status: {response.status_code} - "
                f"Time: {process_time:.4f}s"
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request Failed - ID: {request_id} - Exception: {str(e)} - "
                f"Time: {process_time:.4f}s",
                exc_info=True
            )
            raise e
