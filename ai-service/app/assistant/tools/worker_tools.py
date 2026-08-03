"""
Worker-scoped tools.
Only available via ToolRegistry(role=WORKER). Cannot be reached from customer sessions.
Every tool receives worker_id from context — arguments cannot override it.
"""
import logging
from typing import Any, Dict, List

from app.assistant.tools.base_tool import AssistantTool
from app.utils.backend_client import BackendClient

logger = logging.getLogger(__name__)


class WorkerBookingDetailTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_worker_booking_detail"

    @property
    def description(self) -> str:
        return "Get details of a booking assigned to the authenticated worker — customer instructions, address, scheduled time."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
            },
            "required": ["booking_id"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            worker_id = context.get("worker_id")
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            response = await BackendClient.request(
                "GET",
                f"/api/bookings/{arguments['booking_id']}",
                headers=headers,
            )
            data = response.json()
            # Verify this booking belongs to this worker — structural check
            assigned_worker = data.get("worker_id") or data.get("assigned_worker")
            if assigned_worker and str(assigned_worker) != str(worker_id):
                return {"error": "This booking is not assigned to you."}
            # Return only worker-appropriate fields
            return {
                "booking_id": data.get("_id") or data.get("id"),
                "status": data.get("status"),
                "scheduled_date": data.get("scheduled_date") or data.get("preferred_date"),
                "customer_instructions": data.get("notes") or data.get("booking_notes"),
                "address": data.get("address"),
                "service": data.get("service_name") or data.get("service"),
            }
        except Exception as e:
            logger.error(f"WorkerBookingDetailTool error: {e}")
            return {"error": str(e)}


class WorkerPricingExplanationTool(AssistantTool):
    @property
    def name(self) -> str:
        return "explain_suggested_price"

    @property
    def description(self) -> str:
        return "Explain the AI-suggested pricing for a booking to help the worker set a competitive quotation."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "city": {"type": "string"},
            },
            "required": ["booking_id", "city"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {
                "booking_id": arguments["booking_id"],
                "city": arguments["city"],
            }
            response = await BackendClient.request("POST", "/pricing/estimate", data=payload)
            return response.json()
        except Exception as e:
            logger.error(f"WorkerPricingExplanationTool error: {e}")
            return {"error": str(e)}


class WorkerScheduleTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_worker_schedule"

    @property
    def description(self) -> str:
        return "Get the worker's current schedule and upcoming bookings."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            worker_id = context.get("worker_id")
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            response = await BackendClient.request(
                "GET",
                f"/api/workers/{worker_id}/bookings",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            logger.error(f"WorkerScheduleTool error: {e}")
            return {"error": str(e)}


class WorkerFAQTool(AssistantTool):
    @property
    def name(self) -> str:
        return "search_worker_faqs"

    @property
    def description(self) -> str:
        return "Search the worker FAQ knowledge base for guidance on quotations, policies, and platform usage."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        faqs = context.get("faq_results", [])
        return {"faqs": faqs, "query": arguments["query"]}


class WorkerProfileTipTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_profile_tips"

    @property
    def description(self) -> str:
        return "Get AI-generated tips to improve the worker's profile, rating, and booking acceptance rate."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            worker_id = context.get("worker_id")
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            response = await BackendClient.request(
                "GET",
                f"/api/workers/{worker_id}/profile",
                headers=headers,
            )
            data = response.json()
            tips = []
            if data.get("completion_rate", 100) < 85:
                tips.append("Your completion rate is below 85%. Try to accept only bookings you can fulfill.")
            if data.get("rating", 5) < 4.0:
                tips.append("Your rating is below 4.0. Ask satisfied customers to leave reviews.")
            if not data.get("is_verified"):
                tips.append("Complete profile verification to get more bookings.")
            if not tips:
                tips.append("Your profile looks great! Keep maintaining your high standards.")
            return {"tips": tips, "worker_id": worker_id}
        except Exception as e:
            logger.error(f"WorkerProfileTipTool error: {e}")
            return {"error": str(e)}


def get_worker_tools() -> List[AssistantTool]:
    return [
        WorkerBookingDetailTool(),
        WorkerPricingExplanationTool(),
        WorkerScheduleTool(),
        WorkerFAQTool(),
        WorkerProfileTipTool(),
    ]
