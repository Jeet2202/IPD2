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


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects security headers into every HTTP response.

    Headers added:
        X-Content-Type-Options: nosniff
            Prevents browsers from MIME-sniffing the Content-Type.
            Without this, a browser might treat a JSON response as HTML
            and execute embedded scripts.

        X-Frame-Options: DENY
            Prevents the page from being embedded in iframes.
            Blocks clickjacking attacks where an attacker overlays
            invisible iframes to hijack clicks.

        X-XSS-Protection: 1; mode=block
            Legacy XSS filter for older browsers (Chrome < 78, IE).
            Modern browsers use Content-Security-Policy instead,
            but this is a harmless fallback.

        Strict-Transport-Security: max-age=31536000; includeSubDomains
            Forces HTTPS for 1 year. Browsers will refuse to connect
            over HTTP after seeing this header once. Only effective
            when served over HTTPS (ignored over HTTP).

        Referrer-Policy: strict-origin-when-cross-origin
            Controls what URL info is sent in the Referer header.
            Same-origin requests get the full URL; cross-origin
            requests get only the origin (no path or query string).

        Content-Security-Policy: default-src 'self'
            Restricts where the browser can load resources from.
            'self' means only from the same origin. APIs don't serve
            HTML, so this is a safety net against accidental HTML
            responses being exploited.

        Permissions-Policy: camera=(), microphone=(), geolocation=()
            Disables browser APIs that this API doesn't need.
            Prevents embedded contexts from accessing device features.
    """

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
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response
