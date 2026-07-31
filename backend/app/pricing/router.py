"""
Pricing router.

Endpoints (to be implemented):
    GET    /                 — List pricing for all services
    GET    /{service_type}   — Get pricing for a service type
    PUT    /{service_type}   — Update pricing (admin only)
"""

from fastapi import APIRouter

router = APIRouter()
