from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.sockets import connection_manager, presence_manager
from app.auth.dependencies import get_current_user, get_current_admin
from app.auth.models import User

router = APIRouter()

@router.get(
    "/status",
    summary="Get socket connection status",
    response_description="Returns the real-time infrastructure status.",
)
async def get_socket_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get the health and status of the socket.io server.
    """
    return {
        "status": "healthy",
        "active_users": connection_manager.get_active_users_count(),
        "active_connections": connection_manager.get_active_connections_count(),
    }

@router.get(
    "/connections",
    summary="Get active connections (Admin only)",
    response_description="Returns detailed presence information.",
)
async def get_active_connections(
    current_admin: User = Depends(get_current_admin),
) -> Dict[str, Any]:
    """
    Get detailed presence information for all connected users.
    Requires admin privileges.
    """
    return {
        "total_active_users": connection_manager.get_active_users_count(),
        "total_active_connections": connection_manager.get_active_connections_count(),
        "presence_data": presence_manager.presence_store,
    }
