import logging
from typing import List, Tuple
from app.core.config import settings
from app.models.search_models import IndexableDocument
from app.schemas.search import SearchRequest, SearchResultItem
from app.repositories.search_repository import SearchRepository
from app.services.keyword_search_service import KeywordSearchService
from app.services.semantic_search_service import SemanticSearchService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class HybridSearchService:
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    async def initialize_embeddings(self):
        """Ensures all documents are loaded and have embeddings."""
        docs = await self.repository.load_all_documents()
        docs_to_embed = [d for d in docs if d.embedding is None]
        
        if docs_to_embed:
            logger.info(f"Generating embeddings for {len(docs_to_embed)} documents...")
            texts = [d.text for d in docs_to_embed]
            embeddings = EmbeddingService.generate_embeddings_batch(texts)
            for doc, emb in zip(docs_to_embed, embeddings):
                doc.embedding = emb
            self.repository.update_cache_embeddings(docs)
            logger.info("Embeddings generated and cached.")

    async def search(self, request: SearchRequest) -> Tuple[List[SearchResultItem], int]:
        """
        Execute a hybrid search: semantic + keyword + popularity.
        Returns a tuple of (paginated results, total matching count).
        """
        await self.initialize_embeddings()
        docs = await self.repository.load_all_documents()
        
        # 1. Apply Hard Filters First
        filtered_docs = docs
        if request.filters:
            filtered_docs = self._apply_filters(docs, request.filters)

        if not filtered_docs:
            return [], 0

        # 2. Get Keyword Scores
        keyword_results = KeywordSearchService.search(request.query, filtered_docs)
        keyword_map = {doc.id: score for doc, score in keyword_results}
        
        # 3. Get Semantic Scores
        semantic_results = SemanticSearchService.search(request.query, filtered_docs)
        semantic_map = {doc.id: score for doc, score in semantic_results}
        
        # 4. Combine and Rank
        final_results: List[SearchResultItem] = []
        for doc in filtered_docs:
            kw_score = keyword_map.get(doc.id, 0.0)
            sem_score = semantic_map.get(doc.id, 0.0)
            pop_score = min(1.0, doc.popularity_score / 5.0)
            
            # Weighted Hybrid Score
            hybrid_score = (
                (sem_score * settings.WEIGHT_SEMANTIC) +
                (kw_score * settings.WEIGHT_KEYWORD) +
                (pop_score * settings.WEIGHT_POPULARITY)
            )
            
            # Generate Explanation
            reasons = []
            if kw_score > 0.5: reasons.append("Exact Keyword Match")
            if sem_score > 0.7: reasons.append("Semantically Relevant")
            if pop_score > 0.8: reasons.append("Highly Popular")
            if not reasons: reasons.append("Related Match")

            # Truncate description safely
            description = doc.text[:100] + "..." if len(doc.text) > 100 else doc.text
                
            # Filter out low relevance (threshold 0.2)
            if hybrid_score > 0.2:
                final_results.append(SearchResultItem(
                    item_id=doc.id,
                    item_type=doc.type,
                    title=doc.title,
                    description=description,
                    relevance_score=round(hybrid_score * 100, 2),
                    reasons=reasons,
                    metadata=doc.metadata
                ))
                
        # Sort by relevance descending
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        total = len(final_results)
        
        # 5. Pagination
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        return final_results[start_idx:end_idx], total

    def _apply_filters(self, docs: List[IndexableDocument], filters) -> List[IndexableDocument]:
        result = []
        for doc in docs:
            keep = True
            if filters.category_id and doc.metadata.get("category_id") != filters.category_id:
                keep = False
            if filters.min_rating is not None and doc.metadata.get("rating", 0.0) < filters.min_rating:
                keep = False
            if filters.city and filters.city.lower() not in doc.metadata.get("city", "").lower():
                keep = False
            if filters.is_verified is not None and doc.metadata.get("is_verified") != filters.is_verified:
                keep = False
                
            if keep:
                result.append(doc)
        return result
