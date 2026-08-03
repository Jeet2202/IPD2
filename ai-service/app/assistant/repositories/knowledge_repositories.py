"""
FAQ and Policy repositories — embedding-based retrieval.
Use the same SentenceTransformer already cached by EmbeddingService.
Class-level cache prevents re-loading from DB on every request (same pattern as SearchRepository).
"""
import logging
from typing import List, Dict, Any, Optional

import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class FAQRepository:
    _cache: List[Dict[str, Any]] = []
    _embeddings: Optional[np.ndarray] = None
    _is_loaded: bool = False

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[settings.ASSISTANT_FAQ_COLLECTION]

    async def _ensure_loaded(self):
        if FAQRepository._is_loaded:
            return
        logger.info("Loading FAQ documents into cache...")
        docs = []
        async for doc in self.collection.find({}):
            docs.append({
                "id": str(doc.get("_id")),
                "question": doc.get("question", ""),
                "answer": doc.get("answer", ""),
                "role": doc.get("role", "customer"),  # 'customer' | 'worker' | 'all'
                "text": f"{doc.get('question', '')} {doc.get('answer', '')}",
            })
        if docs:
            texts = [d["text"] for d in docs]
            embeddings = EmbeddingService.generate_embeddings_batch(texts)
            FAQRepository._embeddings = np.array(embeddings)
        FAQRepository._cache = docs
        FAQRepository._is_loaded = True
        logger.info(f"Loaded {len(docs)} FAQ documents")

    async def retrieve(self, query: str, role: str = "customer", top_k: int = None) -> List[Dict[str, Any]]:
        await self._ensure_loaded()
        if not FAQRepository._cache or FAQRepository._embeddings is None:
            return []

        top_k = top_k or settings.ASSISTANT_TOP_K_KNOWLEDGE
        query_emb = EmbeddingService.generate_embedding(query)

        # Cosine similarity
        norms = np.linalg.norm(FAQRepository._embeddings, axis=1)
        q_norm = np.linalg.norm(query_emb)
        with np.errstate(divide="ignore", invalid="ignore"):
            sims = np.dot(FAQRepository._embeddings, query_emb) / (norms * q_norm + 1e-8)

        # Filter by role and get top-k
        results = []
        for i, sim in enumerate(sims):
            doc = FAQRepository._cache[i]
            if doc["role"] in (role, "all") and sim > 0.3:
                results.append({**doc, "score": float(sim)})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @classmethod
    def invalidate_cache(cls):
        cls._cache = []
        cls._embeddings = None
        cls._is_loaded = False


class PolicyRepository:
    _cache: List[Dict[str, Any]] = []
    _embeddings: Optional[np.ndarray] = None
    _is_loaded: bool = False

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[settings.ASSISTANT_POLICY_COLLECTION]

    async def _ensure_loaded(self):
        if PolicyRepository._is_loaded:
            return
        logger.info("Loading policy documents into cache...")
        docs = []
        async for doc in self.collection.find({}):
            docs.append({
                "id": str(doc.get("_id")),
                "topic": doc.get("topic", ""),
                "content": doc.get("content", ""),
                "text": f"{doc.get('topic', '')} {doc.get('content', '')}",
            })
        if docs:
            texts = [d["text"] for d in docs]
            embeddings = EmbeddingService.generate_embeddings_batch(texts)
            PolicyRepository._embeddings = np.array(embeddings)
        PolicyRepository._cache = docs
        PolicyRepository._is_loaded = True
        logger.info(f"Loaded {len(docs)} policy documents")

    async def retrieve(self, topic: str, top_k: int = None) -> List[Dict[str, Any]]:
        await self._ensure_loaded()
        if not PolicyRepository._cache or PolicyRepository._embeddings is None:
            return []

        top_k = top_k or settings.ASSISTANT_TOP_K_KNOWLEDGE
        query_emb = EmbeddingService.generate_embedding(topic)
        norms = np.linalg.norm(PolicyRepository._embeddings, axis=1)
        q_norm = np.linalg.norm(query_emb)
        with np.errstate(divide="ignore", invalid="ignore"):
            sims = np.dot(PolicyRepository._embeddings, query_emb) / (norms * q_norm + 1e-8)

        results = []
        for i, sim in enumerate(sims):
            if sim > 0.3:
                results.append({**PolicyRepository._cache[i], "score": float(sim)})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @classmethod
    def invalidate_cache(cls):
        cls._cache = []
        cls._embeddings = None
        cls._is_loaded = False
