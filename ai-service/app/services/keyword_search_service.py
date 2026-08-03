import re
import logging
from typing import List, Tuple
from app.models.search_models import IndexableDocument
from app.core.config import settings

logger = logging.getLogger(__name__)

# Pre-compiled pattern for word tokenization — applied to sanitized input only
_WORD_PATTERN = re.compile(r'\w+')

class KeywordSearchService:
    @staticmethod
    def search(query: str, documents: List[IndexableDocument]) -> List[Tuple[IndexableDocument, float]]:
        """
        Performs case-insensitive keyword search with partial matching.
        Returns a list of tuples containing the document and its keyword score (0.0 to 1.0).
        """
        if not query or not documents:
            return []

        # Sanitize: strip, lowercase, and limit length to prevent ReDoS via very long inputs
        clean_query = query.strip()[:settings.MAX_QUERY_LENGTH].lower()

        query_terms = set(_WORD_PATTERN.findall(clean_query))
        if not query_terms:
            return []

        results = []
        for doc in documents:
            doc_text = doc.text.lower()
            doc_title = doc.title.lower()
            
            doc_title_words = set(_WORD_PATTERN.findall(doc_title))
            doc_text_words = set(_WORD_PATTERN.findall(doc_text))
            
            score = 0.0
            
            for term in query_terms:
                # Exact word match in title gets highest weight
                if term in doc_title_words:
                    score += 0.5
                # Exact word match in text gets medium weight
                elif term in doc_text_words:
                    score += 0.3
                # Partial (substring) match in title
                elif term in doc_title:
                    score += 0.2
                # Partial (substring) match in text
                elif term in doc_text:
                    score += 0.1
                    
            if score > 0:
                # Normalize score loosely (cap at 1.0)
                results.append((doc, min(1.0, score)))
                
        return sorted(results, key=lambda x: x[1], reverse=True)
