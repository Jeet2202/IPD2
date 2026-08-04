from typing import List, Optional, Tuple
from datetime import datetime, timezone
from beanie.odm.operators.update.general import Set

from .models import DeviceToken, Notification, NotificationPreference

class NotificationRepository:
    
    # --- Device Tokens ---
    
    async def register_token(self, user_id: str, token: str, platform: str) -> DeviceToken:
        """Register a new device token or update an existing one."""
        device = await DeviceToken.find_one({"token": token})
        if device:
            device.user_id = user_id
            device.platform = platform
            device.is_active = True
            device.updated_at = datetime.now(timezone.utc)
            await device.save()
            return device
            
        device = DeviceToken(user_id=user_id, token=token, platform=platform)
        await device.insert()
        return device

    async def update_token(self, user_id: str, old_token: str, new_token: str) -> Optional[DeviceToken]:
        """Update an old token to a new token."""
        device = await DeviceToken.find_one({"token": old_token, "user_id": user_id})
        if device:
            device.token = new_token
            device.updated_at = datetime.now(timezone.utc)
            await device.save()
            return device
        # If old token not found, register new
        return await self.register_token(user_id, new_token, platform="unknown")

    async def remove_token(self, token: str):
        """Remove a device token completely."""
        await DeviceToken.find({"token": token}).delete()

    async def deactivate_token(self, token: str):
        """Mark a token as inactive (e.g. if FCM says it's unregistered)."""
        await DeviceToken.find({"token": token}).update(Set({"is_active": False}))

    async def get_active_tokens(self, user_id: str) -> List[str]:
        """Get all active tokens for a user."""
        devices = await DeviceToken.find({"user_id": user_id, "is_active": True}).to_list()
        return [d.token for d in devices]

    async def get_all_active_tokens(self, target_role: Optional[str] = None) -> List[str]:
        """
        Get all active tokens globally.
        (Note: Target role filtering requires joining with User collection if needed.
         For this phase, if target_role is None, we return all tokens).
        """
        # Note: To filter by role, we would need to look up users with that role.
        # For simplicity in this method, we fetch all. The service layer handles role filtering.
        devices = await DeviceToken.find({"is_active": True}).to_list()
        return [d.token for d in devices]

    # --- Notifications History ---
    
    async def save_notification(self, user_id: str, title: str, body: str, notif_type: str, data: dict = None) -> Notification:
        """Save a notification to the history."""
        notif = Notification(
            user_id=user_id,
            title=title,
            body=body,
            type=notif_type,
            data=data
        )
        await notif.insert()
        return notif
        
    async def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 50) -> Tuple[List[Notification], int]:
        """Get paginated notification history for a user."""
        query = Notification.find({"user_id": user_id})
        total = await query.count()
        items = await query.sort("-created_at").skip(skip).limit(limit).to_list()
        return items, total
        
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark a specific notification as read."""
        notif = await Notification.get(notification_id)
        if notif and notif.user_id == user_id:
            notif.is_read = True
            await notif.save()
            return True
        return False

    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        result = await Notification.find({"user_id": user_id, "is_read": False}).update(Set({"is_read": True}))
        return result.modified_count if result else 0

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a specific notification."""
        notif = await Notification.get(notification_id)
        if notif and notif.user_id == user_id:
            await notif.delete()
            return True
        return False

    async def delete_all_read(self, user_id: str) -> int:
        """Delete all read notifications for a user."""
        result = await Notification.find({"user_id": user_id, "is_read": True}).delete()
        return result.deleted_count if result else 0

    async def get_unread_count(self, user_id: str) -> int:
        """Get the count of unread notifications for a user."""
        return await Notification.find({"user_id": user_id, "is_read": False}).count()

    # --- Preferences ---
    
    async def get_preferences(self, user_id: str) -> NotificationPreference:
        """Get user preferences or create defaults if missing."""
        prefs = await NotificationPreference.find_one({"user_id": user_id})
        if not prefs:
            prefs = NotificationPreference(user_id=user_id)
            await prefs.insert()
        return prefs
        
    async def update_preferences(self, user_id: str, update_data: dict) -> NotificationPreference:
        """Update user preferences."""
        prefs = await self.get_preferences(user_id)
        for key, value in update_data.items():
            if value is not None:
                setattr(prefs, key, value)
        prefs.updated_at = datetime.now(timezone.utc)
        await prefs.save()
        return prefs

notification_repository = NotificationRepository()
