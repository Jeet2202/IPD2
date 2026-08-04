from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- Device Token Schemas ---

class DeviceTokenRequest(BaseModel):
    token: str = Field(..., description="The FCM device token")
    platform: str = Field(default="unknown", description="Platform: ios, android, web")

class DeviceTokenUpdate(BaseModel):
    old_token: str = Field(..., description="The old FCM device token to replace")
    new_token: str = Field(..., description="The new FCM device token")

class DeviceTokenRemove(BaseModel):
    token: str = Field(..., description="The FCM device token to remove")

# --- Notification Schemas ---

class NotificationResponse(BaseModel):
    id: str
    title: str
    body: str
    type: str
    data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

class NotificationListResponse(BaseModel):
    total: int
    items: List[NotificationResponse]

# --- Preference Schemas ---

class PreferencesUpdate(BaseModel):
    booking_notifications: Optional[bool] = None
    chat_notifications: Optional[bool] = None
    ai_notifications: Optional[bool] = None
    promotional_notifications: Optional[bool] = None
    sound: Optional[bool] = None
    vibration: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, description="Format HH:MM")
    quiet_hours_end: Optional[str] = Field(None, description="Format HH:MM")

class PreferencesResponse(BaseModel):
    booking_notifications: bool
    chat_notifications: bool
    ai_notifications: bool
    promotional_notifications: bool
    sound: bool
    vibration: bool
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    updated_at: datetime

# --- Admin Sending Schemas ---

class SendNotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    type: str = "System Announcement"
    data: Optional[Dict[str, Any]] = None

class BroadcastRequest(BaseModel):
    title: str
    body: str
    type: str = "Admin Broadcast"
    data: Optional[Dict[str, Any]] = None
    target_role: Optional[str] = Field(None, description="Optional: Target specific roles (customer, worker). Leave empty for all users.")
