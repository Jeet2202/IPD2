import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
from app.core.config import settings

class AdminExportService:
    @staticmethod
    def ensure_export_dir() -> str:
        # Re-use analytics export dir
        export_dir = settings.ANALYTICS_DATASET_EXPORT_DIR
        os.makedirs(export_dir, exist_ok=True)
        return export_dir

    @staticmethod
    def export_json(data: Dict[str, Any], report_name: str) -> str:
        export_dir = AdminExportService.ensure_export_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"admin_{report_name}_{timestamp}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
            
        return filepath

    @staticmethod
    def export_csv(data: List[Dict[str, Any]], report_name: str) -> str:
        export_dir = AdminExportService.ensure_export_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"admin_{report_name}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        if not data:
            # write empty
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("")
            return filepath
            
        keys = data[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
            
        return filepath
