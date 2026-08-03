from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import List, Optional, Any
import numpy as np

class IndexableDocument(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    type: str = Field(..., description="'service', 'category', or 'worker'")
    text: str = Field(..., description="The full text representation for semantic and keyword search")
    title: str
    popularity_score: float = 0.0
    embedding: Optional[Any] = None  # Will store numpy array at runtime
    metadata: dict = Field(default_factory=dict)
