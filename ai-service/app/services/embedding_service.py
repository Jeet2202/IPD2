import logging
from typing import List, Any
from app.core.config import settings
from app.utils.model_loader import ModelLoader

logger = logging.getLogger(__name__)

class EmbeddingService:
    @classmethod
    def get_model(cls) -> Any:
        return ModelLoader.load_sentence_transformer(settings.EMBEDDING_MODEL_NAME)

    @classmethod
    def generate_embedding(cls, text: str):
        """Generates a single embedding for a given text."""
        model = cls.get_model()
        return model.encode(text, convert_to_numpy=True)

    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]):
        """Generates embeddings for a batch of texts."""
        if not texts:
            return []
        model = cls.get_model()
        return model.encode(texts, convert_to_numpy=True)
