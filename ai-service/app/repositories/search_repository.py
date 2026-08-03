from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any, Optional
import logging
from app.models.search_models import IndexableDocument

logger = logging.getLogger(__name__)

class SearchRepository:
    """
    Class-level cache ensures documents and embeddings survive across requests.
    Without class-level cache, a fresh instance per request would reload all
    documents from MongoDB on every search call.
    """
    _cache: List[IndexableDocument] = []
    _is_loaded: bool = False

    def __init__(self, db: AsyncIOMotorDatabase):
        self.services_col = db["services"]
        self.categories_col = db["categories"]
        self.workers_col = db["workers"]

    async def load_all_documents(self) -> List[IndexableDocument]:
        """
        Loads all categories, services, and workers into a class-level cache.
        Only loads once — subsequent calls return the cache immediately.
        """
        if SearchRepository._is_loaded:
            return SearchRepository._cache

        logger.info("Loading documents into SearchRepository cache...")
        docs: List[IndexableDocument] = []
        
        # Load Categories
        async for cat in self.categories_col.find({"is_active": True}):
            title = cat.get("name", "")
            desc = cat.get("description", "")
            docs.append(IndexableDocument(
                id=str(cat.get("_id")),
                type="category",
                title=title,
                text=f"{title} {desc}",
                metadata={"popularity": cat.get("popularity", 0)}
            ))
            
        # Load Services
        async for svc in self.services_col.find({"is_active": True}):
            title = svc.get("name", "")
            desc = svc.get("description", "")
            tags = " ".join([str(t) for t in svc.get("tags", [])])
            docs.append(IndexableDocument(
                id=str(svc.get("_id")),
                type="service",
                title=title,
                text=f"{title} {desc} {tags}",
                metadata={
                    "price": svc.get("base_price", 0),
                    "category_id": str(svc.get("category_id", ""))
                }
            ))
            
        # Load Workers
        async for wrk in self.workers_col.find({"is_active": True, "is_verified": True}):
            name = wrk.get("name", "Worker")
            rating = wrk.get("rating", 0.0)
            city = wrk.get("address", {}).get("city", "")
            skills = " ".join([str(s) for s in wrk.get("services", [])])
            docs.append(IndexableDocument(
                id=str(wrk.get("_id")),
                type="worker",
                title=name,
                text=f"{name} {skills} {city} rating {rating}",
                popularity_score=float(rating),
                metadata={
                    "rating": float(rating),
                    "city": city,
                    "is_verified": wrk.get("is_verified", False)
                }
            ))
            
        SearchRepository._cache = docs
        SearchRepository._is_loaded = True
        logger.info(f"Loaded {len(SearchRepository._cache)} documents for search.")
        return SearchRepository._cache

    @classmethod
    def update_cache_embeddings(cls, documents: List[IndexableDocument]):
        """Updates the class-level cache with computed embeddings."""
        cls._cache = documents

    @classmethod
    def invalidate_cache(cls):
        """Call this when data changes and re-indexing is needed."""
        cls._cache = []
        cls._is_loaded = False
        logger.info("SearchRepository cache invalidated.")
