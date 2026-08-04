from typing import Any, Dict, Optional
import logging
from .server import sio
from .room_manager import room_manager

logger = logging.getLogger(__name__)

class EventDispatcher:
    """
    Central dispatcher for sending events over Socket.IO.
    Abstracts `sio.emit` and room targeting.
    """
    
    async def dispatch(self, event: str, data: Dict[str, Any], room: Optional[str] = None):
        """
        Generic dispatch method.
        If `room` is provided, emits to that room. Otherwise, broadcasts to all (if allowed).
        """
        try:
            await sio.emit(event, data, room=room)
            logger.debug(f"Emitted event '{event}' to room '{room}' with data: {data}")
        except Exception as e:
            logger.error(f"Failed to emit event '{event}' to room '{room}': {str(e)}")

    async def notify_user(self, user_id: str, event: str, data: Dict[str, Any]):
        """Emit an event specifically to a single user."""
        room = room_manager.get_user_room(user_id)
        await self.dispatch(event, data, room=room)

    async def notify_booking(self, booking_id: str, event: str, data: Dict[str, Any]):
        """Emit an event to all users subscribed to a booking."""
        room = room_manager.get_booking_room(booking_id)
        await self.dispatch(event, data, room=room)

    async def notify_chat(self, booking_id: str, event: str, data: Dict[str, Any]):
        """Emit a chat event to a specific booking chat room."""
        room = room_manager.get_chat_room(booking_id)
        await self.dispatch(event, data, room=room)

    async def notify_admin(self, event: str, data: Dict[str, Any]):
        """Emit an event to all global admins."""
        room = room_manager.get_admin_room()
        await self.dispatch(event, data, room=room)

event_dispatcher = EventDispatcher()
