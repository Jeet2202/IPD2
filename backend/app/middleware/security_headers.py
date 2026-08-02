"""
Security headers middleware.

Adds standard HTTP security headers to every response. These headers
instruct browsers to enforce security policies that prevent common
web attacks.

These headers are defense-in-depth — they don't replace server-side
security, but they prevent browsers from doing unsafe things with
your responses.

Each header is explained inline. All are recommended by OWASP.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects security headers into every HTTP response.

    In development / debug mode, Content-Security-Policy (CSP) allows
    necessary external assets (CDN scripts, stylesheets, fonts, and favicons)
    so FastAPI's Swagger UI (/docs) and ReDoc (/redoc) render correctly.

    In production mode, a strict CSP policy is enforced to protect against
    XSS and data injection attacks.
    """

    @staticmethod
    def _get_csp_policy() -> str:
        """
        Generate Content-Security-Policy header value based on application environment.
        """
        if not settings.is_production or settings.DEBUG:
            # Development / Staging mode: Allow minimum required sources for Swagger UI & ReDoc
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https://fastapi.tiangolo.com https://cdn.jsdelivr.net; "
                "font-src 'self' data: https://fonts.gstatic.com https://cdn.jsdelivr.net; "
                "connect-src 'self';"
            )

        # Production mode: Strict CSP policy
        return (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = self._get_csp_policy()
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response
