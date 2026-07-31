"""
Admin router.

Endpoints (to be implemented):
    GET    /dashboard       — Admin dashboard stats
    GET    /users           — List all users
    PATCH  /users/{user_id} — Update user status (activate/ban)
    GET    /jobs            — List all jobs (admin view)
    GET    /analytics       — Platform analytics
"""

from fastapi import APIRouter

router = APIRouter()
