from typing import List, Dict, Any, Tuple
from app.schemas.analytics import ChartData, ChartDataset

class ChartService:
    @staticmethod
    def format_time_series(data: List[Dict[str, Any]], label_key: str = "_id", value_key: str = "count", dataset_label: str = "Data") -> ChartData:
        """
        Formats generic aggregation output into ChartData schema.
        Expects data in format: [{"_id": "2023-01-01", "count": 5}, ...]
        """
        labels = []
        values = []
        for item in data:
            labels.append(str(item.get(label_key, "")))
            values.append(item.get(value_key, 0))
            
        dataset = ChartDataset(
            label=dataset_label,
            data=values,
            backgroundColor="#4F46E5",
            borderColor="#4F46E5"
        )
        return ChartData(labels=labels, datasets=[dataset])

    @staticmethod
    def format_category_distribution(data: List[Dict[str, Any]]) -> ChartData:
        labels = []
        values = []
        for item in data:
            labels.append(item.get("category_name", "Unknown"))
            values.append(item.get("count", 0))
            
        dataset = ChartDataset(
            label="Category Distribution",
            data=values,
            backgroundColor=["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
        )
        return ChartData(labels=labels, datasets=[dataset])
        
    @staticmethod
    def format_status_distribution(data: Dict[str, int]) -> ChartData:
        labels = list(data.keys())
        values = list(data.values())
        
        dataset = ChartDataset(
            label="Status Distribution",
            data=values,
            backgroundColor=["#10B981", "#3B82F6", "#F59E0B", "#EF4444"]
        )
        return ChartData(labels=labels, datasets=[dataset])
