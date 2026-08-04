import logging

logger = logging.getLogger(__name__)

class RoomManager:
    """
    Manages room names and conventions for Socket.IO.
    Note: Actual joining/leaving is handled by python-socketio's `sio.enter_room()` and `sio.leave_room()`.
    """

    @staticmethod
    def get_user_room(user_id: str) -> str:
        """Room for a specific user to receive private events."""
        return f"user_{user_id}"

    @staticmethod
    def get_booking_room(booking_id: str) -> str:
        """Room for updates regarding a specific booking."""
        return f"booking_{booking_id}"

    @staticmethod
    def get_chat_room(booking_id: str) -> str:
        """Room for chat messages for a specific booking."""
        return f"chat_{booking_id}"

    @staticmethod
    def get_worker_room(worker_id: str) -> str:
        """Room for updates specific to a worker's dashboard or profile."""
        return f"worker_{worker_id}"

    @staticmethod
    def get_admin_room() -> str:
        """Room for global admin notifications."""
        return "admin_global"

room_manager = RoomManager()
