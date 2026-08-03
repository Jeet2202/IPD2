from typing import List, Tuple
import numpy as np
from app.models.search_models import IndexableDocument
from app.services.embedding_service import EmbeddingService

class SemanticSearchService:
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates cosine similarity between two vectors."""
        if vec1 is None or vec2 is None:
            return 0.0
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    @classmethod
    def search(cls, query: str, documents: List[IndexableDocument]) -> List[Tuple[IndexableDocument, float]]:
        """
        Performs semantic search using vector cosine similarity.
        Returns a list of tuples containing the document and its semantic score (0.0 to 1.0).
        """
        if not query or not documents:
            return []

        query_embedding = EmbeddingService.generate_embedding(query)
        
        results = []
        for doc in documents:
            if doc.embedding is not None:
                sim = cls._cosine_similarity(query_embedding, doc.embedding)
                # Normalize cosine similarity [-1, 1] to [0, 1]
                score = (sim + 1.0) / 2.0
                results.append((doc, float(score)))
                
        return sorted(results, key=lambda x: x[1], reverse=True)
