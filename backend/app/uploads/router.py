"""
Uploads router.

Endpoints (to be implemented):
    POST   /image    — Upload an image (Cloudinary)
    POST   /document — Upload a document
    DELETE /{file_id} — Delete uploaded file
"""

from fastapi import APIRouter

router = APIRouter()
