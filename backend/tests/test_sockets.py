import pytest
from app.sockets.connection_manager import ConnectionManager
from app.sockets.presence_manager import PresenceManager
from app.sockets.room_manager import room_manager
from app.sockets.rate_limiter import RateLimiter

def test_connection_manager():
    manager = ConnectionManager()
    
    manager.connect("sid_1", "user_1")
    assert manager.get_user_id("sid_1") == "user_1"
    assert "sid_1" in manager.get_sids("user_1")
    assert manager.get_active_users_count() == 1
    assert manager.get_active_connections_count() == 1
    
    manager.connect("sid_2", "user_1")
    assert manager.get_active_users_count() == 1
    assert manager.get_active_connections_count() == 2
    
    manager.disconnect("sid_1")
    assert manager.get_active_users_count() == 1
    assert manager.get_active_connections_count() == 1
    assert "sid_1" not in manager.get_sids("user_1")
    
    manager.disconnect("sid_2")
    assert manager.get_active_users_count() == 0
    assert manager.get_active_connections_count() == 0

def test_presence_manager():
    manager = PresenceManager()
    
    manager.set_online("user_1", "web", "session_1")
    assert manager.is_online("user_1")
    presence = manager.get_presence("user_1")
    assert presence["active_connections"] == 1
    
    manager.set_online("user_1", "mobile", "session_2")
    presence = manager.get_presence("user_1")
    assert presence["active_connections"] == 2
    
    manager.set_offline("user_1")
    presence = manager.get_presence("user_1")
    assert presence["active_connections"] == 1
    assert manager.is_online("user_1")
    
    manager.set_offline("user_1")
    assert not manager.is_online("user_1")

def test_room_manager():
    assert room_manager.get_user_room("user_123") == "user_user_123"
    assert room_manager.get_booking_room("bk_456") == "booking_bk_456"
    assert room_manager.get_chat_room("bk_456") == "chat_bk_456"
    assert room_manager.get_worker_room("worker_789") == "worker_worker_789"
    assert room_manager.get_admin_room() == "admin_global"

def test_rate_limiter():
    limiter = RateLimiter(limit=2, window_seconds=1)
    
    assert limiter.is_allowed("user_1", "test_event") is True
    assert limiter.is_allowed("user_1", "test_event") is True
    assert limiter.is_allowed("user_1", "test_event") is False # Exceeded limit
    
    # Different user or event should be allowed
    assert limiter.is_allowed("user_2", "test_event") is True
    assert limiter.is_allowed("user_1", "other_event") is True
