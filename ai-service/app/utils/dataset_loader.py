import os
import pandas as pd
import logging
from typing import Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatasetLoader:
    
    @classmethod
    def get_dataset_path(cls, filename: str) -> str:
        """Resolve full dataset path from configured directory"""
        return os.path.join(settings.DATASET_DIRECTORY, filename)

    @classmethod
    def load_csv(cls, filename: str, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load a CSV dataset into a Pandas DataFrame"""
        path = cls.get_dataset_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found: {path}")

        try:
            logger.info(f"Loading CSV dataset from {path}")
            df = pd.read_csv(path)
            
            if required_columns:
                cls._validate_schema(df, required_columns)
                
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV dataset {filename}: {str(e)}")
            raise

    @classmethod
    def load_json(cls, filename: str, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load a JSON dataset into a Pandas DataFrame"""
        path = cls.get_dataset_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found: {path}")

        try:
            logger.info(f"Loading JSON dataset from {path}")
            df = pd.read_json(path)
            
            if required_columns:
                cls._validate_schema(df, required_columns)
                
            return df
        except Exception as e:
            logger.error(f"Failed to load JSON dataset {filename}: {str(e)}")
            raise
            
    @classmethod
    def load_parquet(cls, filename: str, required_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Load a Parquet dataset into a Pandas DataFrame"""
        path = cls.get_dataset_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dataset not found: {path}")

        try:
            logger.info(f"Loading Parquet dataset from {path}")
            df = pd.read_parquet(path)
            
            if required_columns:
                cls._validate_schema(df, required_columns)
                
            return df
        except Exception as e:
            logger.error(f"Failed to load Parquet dataset {filename}: {str(e)}")
            raise

    @classmethod
    def _validate_schema(cls, df: pd.DataFrame, required_columns: List[str]):
        """Validate that all required columns exist in the DataFrame"""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            error_msg = f"Dataset is missing required columns: {missing}"
            logger.error(error_msg)
            raise ValueError(error_msg)
