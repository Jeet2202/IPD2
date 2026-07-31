"""
Reviews router.

Endpoints (to be implemented):
    POST   /                — Create a review for a completed job
    GET    /worker/{worker_id} — List reviews for a worker
    GET    /{review_id}     — Get review details
    DELETE /{review_id}     — Delete own review
"""

from fastapi import APIRouter

router = APIRouter()
