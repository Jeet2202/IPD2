import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.notifications.service import notification_service
from app.notifications.templates import get_notification_template, NotificationType
from app.notifications.models import NotificationPreference

def test_notification_templates():
    title, body = get_notification_template(NotificationType.BOOKING_CREATED, {"service_name": "Plumbing"})
    assert title == "New Booking Request"
    assert "Plumbing" in body
    
    title, body = get_notification_template(NotificationType.WORKER_ARRIVING, {"worker_name": "John Doe"})
    assert title == "Worker is Arriving"
    assert "John Doe" in body

@pytest.mark.asyncio
@patch("app.notifications.service.notification_repository")
async def test_register_device(mock_repo):
    mock_repo.register_token = AsyncMock()
    await notification_service.register_device("user1", "token123", "ios")
    mock_repo.register_token.assert_called_once_with("user1", "token123", "ios")

def test_preferences_check():
    # Test preferences logic inside service using a simple mock
    prefs = MagicMock()
    prefs.user_id = "test"
    prefs.booking_notifications = False
    prefs.ai_notifications = True
    
    # Should block booking created because booking_notifications=False
    assert not notification_service._is_allowed_by_preferences(NotificationType.BOOKING_CREATED, prefs)
    
    # Should allow AI
    assert notification_service._is_allowed_by_preferences(NotificationType.AI_RECOMMENDATION, prefs)
    
    # Should always allow admin broadcast
    assert notification_service._is_allowed_by_preferences(NotificationType.ADMIN_BROADCAST, prefs)

@pytest.mark.asyncio
@patch("app.notifications.service.fcm_client")
@patch("app.notifications.service.notification_repository")
async def test_process_single_notification(mock_repo, mock_fcm):
    pref_mock = MagicMock()
    pref_mock.booking_notifications = True
    mock_repo.get_preferences = AsyncMock(return_value=pref_mock)
    mock_repo.save_notification = AsyncMock()
    mock_repo.get_active_tokens = AsyncMock(return_value=["token1"])
    
    mock_fcm.send_multicast = MagicMock(return_value=(1, 0, []))
    
    await notification_service._process_single_notification("user1", NotificationType.BOOKING_COMPLETED, {"service_name": "Cleaning"})
    
    mock_repo.get_active_tokens.assert_called_once_with("user1")
    mock_fcm.send_multicast.assert_called_once()
    
    args, kwargs = mock_fcm.send_multicast.call_args
    assert args[0] == ["token1"]
    assert args[1] == "Booking Completed"
