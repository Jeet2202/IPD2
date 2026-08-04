import httpx
import logging
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class BackendClient:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                base_url=settings.BACKEND_BASE_URL,
                timeout=settings.REQUEST_TIMEOUT,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.aclose()
            cls._client = None
            logger.info("Backend HTTP client closed")

    @classmethod
    async def request(
        cls, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """Make an asynchronous HTTP request to the main Ally backend"""
        client = cls.get_client()
        
        # Prepare headers (e.g. inject generic auth if needed later)
        req_headers = headers or {}
        req_headers.setdefault("Content-Type", "application/json")

        try:
            logger.debug(f"Sending {method} request to backend endpoint: {endpoint}")
            response = await client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
                headers=req_headers
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"Backend HTTP error for {endpoint}: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Backend request error for {endpoint}: {str(e)}")
            raise
