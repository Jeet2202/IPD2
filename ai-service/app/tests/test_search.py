import pytest
import numpy as np
from app.models.search_models import IndexableDocument
from app.services.keyword_search_service import KeywordSearchService
from app.services.semantic_search_service import SemanticSearchService
from app.schemas.search import SearchRequest, SearchFilters
from app.services.hybrid_search_service import HybridSearchService
from app.repositories.search_repository import SearchRepository

@pytest.fixture(autouse=True)
def reset_search_cache():
    """Ensure class-level cache is clean between tests to avoid state leak."""
    SearchRepository.invalidate_cache()
    yield
    SearchRepository.invalidate_cache()

@pytest.fixture
def mock_documents():
    return [
        IndexableDocument(
            id="1",
            type="service",
            title="Plumbing Repair",
            text="Plumbing Repair Fix leaky pipes and faucets plumber",
            popularity_score=4.5,
            metadata={"category_id": "cat1", "price": 500, "city": "Mumbai"}
        ),
        IndexableDocument(
            id="2",
            type="service",
            title="AC Servicing",
            text="AC Servicing Clean and repair air conditioning units",
            popularity_score=4.8,
            metadata={"category_id": "cat2", "price": 800, "city": "Delhi"}
        )
    ]

def test_keyword_search(mock_documents):
    # Exact word match in text
    results = KeywordSearchService.search("plumber", mock_documents)
    assert len(results) == 1
    assert results[0][0].id == "1"
    
    # Partial (substring) match
    results = KeywordSearchService.search("plumb", mock_documents)
    assert len(results) == 1
    assert results[0][0].id == "1"
    
    # Case insensitive
    results = KeywordSearchService.search("AC SERVICING", mock_documents)
    assert len(results) == 1
    assert results[0][0].id == "2"

def test_keyword_search_query_sanitation():
    """Query exceeding MAX_QUERY_LENGTH should be truncated and not crash."""
    docs = [IndexableDocument(id="x", type="service", title="Test", text="test service")]
    long_query = "a" * 10000
    results = KeywordSearchService.search(long_query, docs)
    # Should return empty (no match) without error
    assert isinstance(results, list)

def test_cosine_similarity():
    vec1 = np.array([1.0, 0.0, 0.0])
    vec2 = np.array([1.0, 0.0, 0.0])
    vec3 = np.array([0.0, 1.0, 0.0])
    
    sim_same = SemanticSearchService._cosine_similarity(vec1, vec2)
    assert np.isclose(sim_same, 1.0)
    
    sim_diff = SemanticSearchService._cosine_similarity(vec1, vec3)
    assert np.isclose(sim_diff, 0.0)

class MockSearchRepository:
    """In-test mock — bypasses DB and uses provided docs directly."""
    def __init__(self, docs):
        self.docs = docs
        
    async def load_all_documents(self):
        return self.docs
        
    @classmethod
    def update_cache_embeddings(cls, docs):
        pass

    @classmethod
    def invalidate_cache(cls):
        pass

@pytest.mark.asyncio
async def test_hybrid_search_filters(mock_documents):
    """Real embeddings generated via SentenceTransformer; filters applied on top."""
    repo = MockSearchRepository(mock_documents)
    service = HybridSearchService(repo)
    
    # Test Category Filter — only doc with category_id="cat1" should be returned
    req = SearchRequest(query="repair", filters=SearchFilters(category_id="cat1"))
    results, total = await service.search(req)
    
    assert total == 1
    assert results[0].item_id == "1"
    
    # Test City Filter — only doc with city="Delhi" should be returned
    req = SearchRequest(query="repair", filters=SearchFilters(city="Delhi"))
    results, total = await service.search(req)
    
    assert total == 1
    assert results[0].item_id == "2"

@pytest.mark.asyncio
async def test_hybrid_search_empty_results(mock_documents):
    """Category filter that matches nothing should return empty list, not error."""
    repo = MockSearchRepository(mock_documents)
    service = HybridSearchService(repo)

    req = SearchRequest(query="plumber", filters=SearchFilters(category_id="nonexistent_cat"))
    results, total = await service.search(req)
    assert results == []
    assert total == 0

@pytest.mark.asyncio
async def test_hybrid_search_pagination(mock_documents):
    """Verify pagination slices results correctly."""
    repo = MockSearchRepository(mock_documents)
    service = HybridSearchService(repo)

    # Both docs match "repair" — page 1, size 1 should return exactly 1
    req = SearchRequest(query="repair", page=1, page_size=1)
    results, total = await service.search(req)
    assert len(results) == 1
    assert total >= 1
