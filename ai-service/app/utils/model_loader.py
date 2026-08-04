import os
import joblib
import pickle
import logging
from typing import Any, Dict
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class ModelLoader:
    _cache: Dict[str, Any] = {}

    @classmethod
    def get_model_path(cls, model_filename: str) -> str:
        """Resolve full model path from configured directory"""
        return os.path.join(settings.MODEL_DIRECTORY, model_filename)

    @classmethod
    def load_joblib(cls, model_filename: str) -> Any:
        """Load and cache a Joblib model"""
        if model_filename in cls._cache:
            return cls._cache[model_filename]

        path = cls.get_model_path(model_filename)
        if not os.path.exists(path):
            logger.error(f"Joblib model not found at path: {path}")
            raise FileNotFoundError(f"Model not found: {path}")

        try:
            logger.info(f"Loading Joblib model from {path}")
            model = joblib.load(path)
            cls._cache[model_filename] = model
            logger.info(f"Audit: [MODEL_LOADED] entity_id={model_filename} details=joblib")
            return model
        except Exception as e:
            logger.error(f"Failed to load Joblib model {model_filename}: {str(e)}")
            raise

    @classmethod
    def load_pickle(cls, model_filename: str) -> Any:
        """Load and cache a Pickle model"""
        if model_filename in cls._cache:
            return cls._cache[model_filename]

        path = cls.get_model_path(model_filename)
        if not os.path.exists(path):
            logger.error(f"Pickle model not found at path: {path}")
            raise FileNotFoundError(f"Model not found: {path}")

        try:
            logger.info(f"Loading Pickle model from {path}")
            with open(path, 'rb') as f:
                model = pickle.load(f)
            cls._cache[model_filename] = model
            logger.info(f"Audit: [MODEL_LOADED] entity_id={model_filename} details=pickle")
            return model
        except Exception as e:
            logger.error(f"Failed to load Pickle model {model_filename}: {str(e)}")
            raise

    @classmethod
    def load_sentence_transformer(cls, model_name: str) -> SentenceTransformer:
        """Load and cache a SentenceTransformer model (from HuggingFace/local)"""
        if model_name in cls._cache:
            return cls._cache[model_name]

        try:
            logger.info(f"Loading SentenceTransformer model: {model_name}")
            model = SentenceTransformer(model_name)
            cls._cache[model_name] = model
            logger.info(f"Audit: [MODEL_LOADED] entity_id={model_name} details=sentence-transformer")
            return model
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model {model_name}: {str(e)}")
            raise
            
    @classmethod
    def clear_cache(cls):
        """Clear the model cache"""
        for model_name in cls._cache.keys():
            logger.info(f"Audit: [MODEL_UNLOADED] entity_id={model_name}")
        cls._cache.clear()
        logger.info("Model cache cleared")

    @classmethod
    def get_loaded_models(cls) -> list[str]:
        """Return list of currently loaded model names"""
        return list(cls._cache.keys())
