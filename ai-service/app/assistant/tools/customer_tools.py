"""
Customer-scoped tools.
These are the ONLY tools available to the Customer assistant.
All calls go through BackendClient or existing AI endpoints — no direct DB writes.
"""
import json
import logging
from typing import Any, Dict, List

from app.assistant.tools.base_tool import AssistantTool
from app.utils.backend_client import BackendClient

logger = logging.getLogger(__name__)


class ServiceSearchTool(AssistantTool):
    @property
    def name(self) -> str:
        return "search_services"

    @property
    def description(self) -> str:
        return "Search for available services and workers on the KaamSetu platform using a natural language query."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query, e.g. 'plumber near me'"},
                "city": {"type": "string", "description": "City to search in"},
            },
            "required": ["query"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {"query": arguments["query"], "page": 1, "page_size": 5}
            if arguments.get("city"):
                payload["filters"] = {"city": arguments["city"]}
            response = await BackendClient.request("POST", "/services/search", data=payload)
            return response.json()
        except Exception as e:
            logger.error(f"ServiceSearchTool error: {e}")
            return {"error": str(e), "results": []}


class BookingStatusTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_booking_status"

    @property
    def description(self) -> str:
        return "Get the current status and details of a customer booking by booking ID."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string", "description": "The booking ID to look up"},
            },
            "required": ["booking_id"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            auth_token = context.get("auth_token", "")
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            response = await BackendClient.request(
                "GET",
                f"/api/bookings/{arguments['booking_id']}",
                headers=headers,
            )
            data = response.json()
            # Return only customer-safe fields — strip worker contact details
            safe = {
                "booking_id": data.get("_id") or data.get("id"),
                "status": data.get("status"),
                "service": data.get("service_name") or data.get("service"),
                "scheduled_date": data.get("scheduled_date") or data.get("preferred_date"),
                "created_at": data.get("created_at"),
            }
            return safe
        except Exception as e:
            logger.error(f"BookingStatusTool error: {e}")
            return {"error": str(e)}


class PriceEstimateTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_price_estimate"

    @property
    def description(self) -> str:
        return "Get an AI-generated price estimate for a booking. Returns estimated price, range, and confidence."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "city": {"type": "string"},
                "urgency_level": {
                    "type": "string",
                    "enum": ["normal", "high", "critical"],
                    "default": "normal",
                },
                "estimated_duration_hours": {"type": "number", "default": 1.0},
            },
            "required": ["booking_id", "city"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {
                "booking_id": arguments["booking_id"],
                "city": arguments["city"],
                "urgency_level": arguments.get("urgency_level", "normal"),
                "estimated_duration_hours": arguments.get("estimated_duration_hours", 1.0),
            }
            response = await BackendClient.request("POST", "/pricing/estimate", data=payload)
            return response.json()
        except Exception as e:
            logger.error(f"PriceEstimateTool error: {e}")
            return {"error": str(e)}


class RecommendationExplanationTool(AssistantTool):
    @property
    def name(self) -> str:
        return "explain_recommendations"

    @property
    def description(self) -> str:
        return "Retrieve the top recommended workers for a booking and their recommendation reasons."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "booking_id": {"type": "string"},
                "max_results": {"type": "integer", "default": 3},
            },
            "required": ["booking_id"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            payload = {
                "booking_id": arguments["booking_id"],
                "max_results": arguments.get("max_results", 3),
            }
            response = await BackendClient.request("POST", "/recommendations/workers", data=payload)
            data = response.json()
            # Scrub worker contact details — customer sees only reasons and ranking
            recommendations = []
            for rec in data.get("recommendations", []):
                recommendations.append({
                    "ranking": rec.get("ranking"),
                    "reasons": rec.get("reasons"),
                    "distance_km": rec.get("distance_km"),
                    "estimated_arrival_mins": rec.get("estimated_arrival_mins"),
                    "confidence": rec.get("confidence"),
                })
            return {"booking_id": data.get("booking_id"), "recommendations": recommendations}
        except Exception as e:
            logger.error(f"RecommendationExplanationTool error: {e}")
            return {"error": str(e)}


class FAQTool(AssistantTool):
    @property
    def name(self) -> str:
        return "search_faqs"

    @property
    def description(self) -> str:
        return "Search the KaamSetu FAQ knowledge base for answers to common customer questions."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The question to find an answer for"},
            },
            "required": ["query"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # KnowledgeRetriever is injected at pipeline level and results are passed via context
        faqs = context.get("faq_results", [])
        return {"faqs": faqs, "query": arguments["query"]}


class PolicyTool(AssistantTool):
    @property
    def name(self) -> str:
        return "get_policy"

    @property
    def description(self) -> str:
        return "Retrieve platform policy information — cancellation, payment, refunds, safety."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Policy topic, e.g. 'cancellation', 'payment', 'refund', 'safety'",
                },
            },
            "required": ["topic"],
        }

    async def execute(self, arguments: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        policies = context.get("policy_results", [])
        return {"policies": policies, "topic": arguments["topic"]}


def get_customer_tools() -> List[AssistantTool]:
    return [
        ServiceSearchTool(),
        BookingStatusTool(),
        PriceEstimateTool(),
        RecommendationExplanationTool(),
        FAQTool(),
        PolicyTool(),
    ]
