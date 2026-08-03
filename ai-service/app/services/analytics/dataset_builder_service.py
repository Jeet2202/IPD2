from typing import List, Dict, Any
from datetime import datetime

class DatasetBuilderService:
    @staticmethod
    def flatten_booking_dataset(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        flattened = []
        for item in raw_data:
            # Flatten or transform raw MongoDB documents for ML readiness
            flat = {
                "booking_id": str(item.get("_id", "")),
                "user_id": item.get("user_id", ""),
                "worker_id": item.get("assigned_worker_id", ""),
                "service_id": item.get("service_id", ""),
                "category_id": item.get("category_id", ""),
                "status": item.get("status", ""),
                "final_price": item.get("final_price", 0.0),
                "created_at": item.get("created_at", ""),
                "completed_at": item.get("completed_at", "")
            }
            
            # Simple feature engineering hook
            if flat["created_at"]:
                try:
                    dt = datetime.fromisoformat(str(flat["created_at"]).replace('Z', '+00:00'))
                    flat["day_of_week"] = dt.weekday()
                    flat["is_weekend"] = 1 if dt.weekday() >= 5 else 0
                    flat["hour_of_day"] = dt.hour
                except Exception:
                    pass
                    
            flattened.append(flat)
            
        return flattened
