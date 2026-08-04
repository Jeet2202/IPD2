import time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Basic in-memory rate limiter for socket events.
    Tracks requests per user and event type within a time window.
    """
    def __init__(self, limit: int = 10, window_seconds: int = 1):
        self.limit = limit
        self.window_seconds = window_seconds
        # Maps (user_id, event) -> (count, window_start_time)
        self.records: Dict[Tuple[str, str], Tuple[int, float]] = {}

    def is_allowed(self, user_id: str, event: str) -> bool:
        """Check if the user is allowed to emit the event based on rate limits."""
        now = time.time()
        key = (user_id, event)
        
        if key not in self.records:
            self.records[key] = (1, now)
            return True
            
        count, window_start = self.records[key]
        
        if now - window_start > self.window_seconds:
            # Reset window
            self.records[key] = (1, now)
            return True
            
        if count >= self.limit:
            logger.warning(f"Rate limit exceeded for user {user_id} on event '{event}'")
            return False
            
        # Increment count
        self.records[key] = (count + 1, window_start)
        return True

rate_limiter = RateLimiter(limit=20, window_seconds=1) # Default 20 events per second per event type per user
