from typing import Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class PresenceManager:
    """
    Manages presence information for users (online, offline, last seen).
    Currently implemented in-memory. Can be backed by Redis in the future.
    """
    def __init__(self):
        # Maps user_id to presence data dictionary
        self.presence_store: Dict[str, Dict[str, Any]] = {}

    def set_online(self, user_id: str, device_type: str = "unknown", session_id: str = ""):
        """Mark a user as online."""
        if user_id not in self.presence_store:
            self.presence_store[user_id] = {
                "status": "online",
                "last_seen": datetime.now(timezone.utc).isoformat(),
                "active_connections": 1,
                "device_types": {device_type},
                "session_ids": {session_id} if session_id else set()
            }
        else:
            self.presence_store[user_id]["status"] = "online"
            self.presence_store[user_id]["active_connections"] += 1
            self.presence_store[user_id]["device_types"].add(device_type)
            if session_id:
                self.presence_store[user_id]["session_ids"].add(session_id)
            self.presence_store[user_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
        
        logger.debug(f"User {user_id} presence updated to online.")

    def set_offline(self, user_id: str, device_type: str = "unknown", session_id: str = ""):
        """Decrement connection count and mark user as offline if 0."""
        if user_id in self.presence_store:
            self.presence_store[user_id]["active_connections"] = max(0, self.presence_store[user_id]["active_connections"] - 1)
            
            # Note: We are not removing device_types/session_ids here immediately to keep last known, 
            # or we could remove specific ones if passed correctly. 
            # For a robust system, these should be tied to the `sid`.
            
            if self.presence_store[user_id]["active_connections"] == 0:
                self.presence_store[user_id]["status"] = "offline"
                self.presence_store[user_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
                logger.debug(f"User {user_id} presence updated to offline.")

    def get_presence(self, user_id: str) -> Dict[str, Any]:
        """Get presence data for a user."""
        return self.presence_store.get(user_id, {
            "status": "offline",
            "last_seen": None,
            "active_connections": 0,
            "device_types": set(),
            "session_ids": set()
        })

    def is_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return self.get_presence(user_id).get("status") == "online"

presence_manager = PresenceManager()
