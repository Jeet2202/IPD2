"""
Authentication FastAPI Router — endpoints for Auth, Sessions, Passwords, and OTP Verification.

Architecture:
    - Route handling layer — request validation, status codes, OpenAPI documentation, and response serialization.
    - Zero business logic and zero database queries inside routes.
    - Delegates execution to AuthService.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Request, status

from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MeResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResendEmailOTPRequest,
    ResetPasswordRequest,
    SuccessResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyPasswordResetOTPRequest,
    VerifyPhoneRequest,
)
from app.auth.service import AuthService
from app.core.dependencies import CurrentUserDep
from app.core.exceptions import AppException

router = APIRouter()
