"""
Notifications router.

Endpoints (to be implemented):
    GET    /me               — List current user's notifications
    PATCH  /{notification_id}/read — Mark as read
    POST   /me/read-all      — Mark all as read
"""

from fastapi import APIRouter

router = APIRouter()
