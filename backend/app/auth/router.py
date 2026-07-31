"""
Authentication router.

Endpoints (to be implemented):
    POST /register     — Register new user (phone + OTP)
    POST /login        — Login with credentials
    POST /refresh      — Refresh access token
    POST /logout       — Invalidate refresh token
    POST /verify-otp   — Verify OTP code
"""

from fastapi import APIRouter

router = APIRouter()
