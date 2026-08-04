from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps sid to user_id
        self.sid_to_user: Dict[str, str] = {}
        # Maps user_id to a set of sids (since a user can have multiple connections/devices)
        self.user_to_sids: Dict[str, set[str]] = {}

    def connect(self, sid: str, user_id: str):
        """Register a new connection."""
        self.sid_to_user[sid] = user_id
        if user_id not in self.user_to_sids:
            self.user_to_sids[user_id] = set()
        self.user_to_sids[user_id].add(sid)
        logger.debug(f"User {user_id} connected with sid {sid}")

    def disconnect(self, sid: str) -> Optional[str]:
        """Unregister a connection. Returns the user_id if found."""
        user_id = self.sid_to_user.pop(sid, None)
        if user_id:
            sids = self.user_to_sids.get(user_id, set())
            sids.discard(sid)
            if not sids:
                self.user_to_sids.pop(user_id, None)
            logger.debug(f"User {user_id} disconnected sid {sid}")
            return user_id
        return None

    def get_user_id(self, sid: str) -> Optional[str]:
        """Get the user_id for a given sid."""
        return self.sid_to_user.get(sid)

    def get_sids(self, user_id: str) -> set[str]:
        """Get all active sids for a given user_id."""
        return self.user_to_sids.get(user_id, set())

    def get_active_users_count(self) -> int:
        """Get the total number of unique active users."""
        return len(self.user_to_sids)

    def get_active_connections_count(self) -> int:
        """Get the total number of active connections."""
        return len(self.sid_to_user)

connection_manager = ConnectionManager()
