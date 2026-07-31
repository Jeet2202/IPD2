"""
Inspection router.

Endpoints (to be implemented):
    POST   /                   — Create inspection request
    GET    /                   — List inspections
    GET    /{inspection_id}    — Get inspection details
    PATCH  /{inspection_id}    — Update inspection status
"""

from fastapi import APIRouter

router = APIRouter()
