"""
Worker router.

Endpoints (to be implemented):
    GET    /me           — Get current worker profile
    PUT    /me           — Update current worker profile
    GET    /             — List available workers (public)
    GET    /{worker_id}  — Get worker by ID (public)
    PATCH  /me/status    — Toggle availability status
"""

from fastapi import APIRouter

router = APIRouter()
