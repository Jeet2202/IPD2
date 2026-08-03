import os
import json
import csv
import uuid
from datetime import datetime
from typing import List, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class ExportService:
    @staticmethod
    def ensure_export_dir():
        os.makedirs(settings.ANALYTICS_DATASET_EXPORT_DIR, exist_ok=True)

    @staticmethod
    def export_csv(data: List[Dict[str, Any]], entity: str) -> str:
        ExportService.ensure_export_dir()
        filename = f"{entity}_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.csv"
        filepath = os.path.join(settings.ANALYTICS_DATASET_EXPORT_DIR, filename)
        
        if not data:
            with open(filepath, 'w', newline='') as f:
                f.write("")
            return filepath
            
        keys = list(data[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
            
        logger.info(f"Exported {len(data)} records to {filepath}")
        return filepath

    @staticmethod
    def export_json(data: List[Dict[str, Any]], entity: str) -> str:
        ExportService.ensure_export_dir()
        filename = f"{entity}_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}.json"
        filepath = os.path.join(settings.ANALYTICS_DATASET_EXPORT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        logger.info(f"Exported {len(data)} records to {filepath}")
        return filepath
