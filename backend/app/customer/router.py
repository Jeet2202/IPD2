"""
Customer router.

Endpoints (to be implemented):
    GET    /me          — Get current customer profile
    PUT    /me          — Update current customer profile
    GET    /me/bookings — List customer's bookings
    DELETE /me          — Deactivate customer account
"""

from fastapi import APIRouter

router = APIRouter()
