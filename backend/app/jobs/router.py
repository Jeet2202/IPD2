"""
Jobs router.

Endpoints (to be implemented):
    POST   /             — Create a new job
    GET    /             — List jobs (filtered by status, location)
    GET    /{job_id}     — Get job details
    PUT    /{job_id}     — Update job
    PATCH  /{job_id}     — Cancel job
    POST   /{job_id}/accept — Worker accepts job
"""

from fastapi import APIRouter

router = APIRouter()
