"""
Service Model Re-export.
"""

from app.category.models import Service, generate_slug

__all__ = ["Service", "generate_slug"]
