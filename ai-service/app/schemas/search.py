from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class SearchFilters(BaseModel):
    category_id: Optional[str] = None
    service_id: Optional[str] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    is_verified: Optional[bool] = None

class SearchRequest(BaseModel):
    query: str = Field(..., description="The natural language search query")
    filters: Optional[SearchFilters] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)

class SearchResultItem(BaseModel):
    item_id: str
    item_type: str = Field(..., description="'service' or 'worker'")
    title: str
    description: Optional[str] = None
    relevance_score: float
    reasons: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total: int
    page: int
    page_size: int

class SearchSuggestionModel(BaseModel):
    suggestion: str
    type: str = Field(..., description="'recent', 'trending', or 'autocomplete'")

class SearchHistoryModel(BaseModel):
    query: str
    timestamp: str
    user_id: Optional[str] = None
