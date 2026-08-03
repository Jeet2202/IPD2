"""
Admin-scoped tools.
Only reachable via ToolRegistry(role=ADMIN). Middleware also enforces role=admin.
Returns aggregated/anonymized data — never raw PII.
"""
import logging
from typing import Any, Dict, List

from app.assistant.tools.base_tool import AssistantTool
from app.utils.backend_client import BackendClient

logger = logging.getLogger(__name__)


class PlatformStatsTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_platform_stats"

    @property
    def description(self) -> str:
        return "Retrieve high-level platform statistics: total bookings, active workers, revenue summary."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["today", "week", "month", "all"],
                    "default": "month",
                }
            },
            "required": [],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            period = arguments.get("period", "month")
            response = await BackendClient.request(
                "GET", f"/api/admin/stats?period={period}", headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"PlatformStatsTool error: {e}")
            return {"error": str(e)}


class WorkerInsightTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_worker_insights"

    @property
    def description(self) -> str:
        return "Get aggregated worker performance insights: top performers, churn risk, verification backlog."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "Filter by city (optional)"},
            },
            "required": [],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            params = {}
            if arguments.get("city"):
                params["city"] = arguments["city"]
            response = await BackendClient.request(
                "GET", "/api/admin/workers/insights", params=params, headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"WorkerInsightTool error: {e}")
            return {"error": str(e)}


class BookingAnalyticsTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_booking_analytics"

    @property
    def description(self) -> str:
        return "Get booking volume trends, cancellation rates, and service category breakdown."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {"type": "string", "enum": ["week", "month", "quarter"], "default": "month"},
                "category_id": {"type": "string", "description": "Filter by category (optional)"},
            },
            "required": [],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            params = {"period": arguments.get("period", "month")}
            if arguments.get("category_id"):
                params["category_id"] = arguments["category_id"]
            response = await BackendClient.request(
                "GET", "/api/admin/bookings/analytics", params=params, headers=headers
            )
            return response.json()
        except Exception as e:
            logger.error(f"BookingAnalyticsTool error: {e}")
            return {"error": str(e)}


class SystemHealthTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_system_health"

    @property
    def description(self) -> str:
        return "Check AI service health, database connectivity, and model status."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Call our own health endpoint
            response = await BackendClient.request("GET", "/health")
            return response.json()
        except Exception as e:
            logger.error(f"SystemHealthTool error: {e}")
            return {"error": str(e), "status": "unknown"}


def get_admin_tools() -> List[AssistantTool]:
    return [
        PlatformStatsTool(),
        WorkerInsightTool(),
        BookingAnalyticsTool(),
        SystemHealthTool(),
    ]
