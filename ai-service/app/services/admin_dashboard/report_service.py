from typing import List, Dict, Any
from app.repositories.admin_dashboard.report_repository import ReportRepository
from app.services.admin_dashboard.export_service import AdminExportService
from app.schemas.admin_dashboard import ExportResponse
import json

class ReportService:
    def __init__(self, report_repo: ReportRepository):
        self.report_repo = report_repo

    async def generate_report(self, report_name: str, format_type: str, data: Any) -> ExportResponse:
        
        if format_type.lower() == 'csv':
            # Data should be a list of dicts for CSV
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                filepath = AdminExportService.export_csv(data, report_name)
                record_count = len(data)
            else:
                raise ValueError("Data must be a list of dictionaries for CSV export.")
        else:
            # JSON format
            # ensure serializable
            try:
                dict_data = data if isinstance(data, dict) else json.loads(data.json())
            except AttributeError:
                dict_data = {"data": data}
                
            filepath = AdminExportService.export_json(dict_data, report_name)
            record_count = len(data) if isinstance(data, list) else 1

        response = ExportResponse(
            status="success",
            message=f"Report {report_name} exported successfully in {format_type} format.",
            file_path=filepath,
            record_count=record_count
        )
        
        await self.report_repo.save_report(response)
        return response
