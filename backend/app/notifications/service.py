import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import BackgroundTasks

from .repository import notification_repository
from .fcm_client import fcm_client
from .templates import get_notification_template, NotificationType
from .models import NotificationPreference
from app.auth.models import User

logger = logging.getLogger(__name__)

class NotificationService:
    
    # --- Device Token Management ---
    
    async def register_device(self, user_id: str, token: str, platform: str):
        return await notification_repository.register_token(user_id, token, platform)
        
    async def update_device(self, user_id: str, old_token: str, new_token: str):
        return await notification_repository.update_token(user_id, old_token, new_token)
        
    async def remove_device(self, token: str):
        await notification_repository.remove_token(token)

    # --- Preferences ---
    
    async def get_preferences(self, user_id: str) -> NotificationPreference:
        return await notification_repository.get_preferences(user_id)
        
    async def update_preferences(self, user_id: str, update_data: dict) -> NotificationPreference:
        return await notification_repository.update_preferences(user_id, update_data)

    # --- Send Logic (Queue & Execution) ---

    def queue_notification(self, background_tasks: BackgroundTasks, user_id: str, notif_type: str, data: Dict[str, Any] = None):
        """
        Enqueue a single notification to be sent in the background.
        """
        background_tasks.add_task(self._process_single_notification, user_id, notif_type, data)

    def queue_broadcast(self, background_tasks: BackgroundTasks, title: str, body: str, target_role: Optional[str] = None):
        """
        Enqueue a broadcast notification.
        """
        background_tasks.add_task(self._process_broadcast, title, body, target_role)

    async def _process_single_notification(self, user_id: str, notif_type: str, data: Dict[str, Any] = None):
        """Background task to resolve template, check preferences, save to DB, and send via FCM."""
        try:
            # 1. Check Preferences
            prefs = await notification_repository.get_preferences(user_id)
            if not self._is_allowed_by_preferences(notif_type, prefs):
                logger.info(f"Notification '{notif_type}' skipped for user {user_id} due to preferences.")
                return

            # 2. Build Template
            title, body = get_notification_template(notif_type, data)
            
            # 3. Save to DB (Metadata only)
            await notification_repository.save_notification(user_id, title, body, notif_type, data)
            
            # 4. Fetch Tokens
            tokens = await notification_repository.get_active_tokens(user_id)
            if not tokens:
                logger.info(f"No active tokens found for user {user_id}.")
                return
                
            # 5. Send via FCM with basic retry
            await self._send_with_retry(tokens, title, body, data)
            
        except Exception as e:
            logger.error(f"Error processing single notification for user {user_id}: {e}")

    async def _process_broadcast(self, title: str, body: str, target_role: Optional[str] = None):
        """Background task to broadcast to all/filtered users."""
        try:
            if target_role:
                # Filter by role: find user IDs with the given role, then fetch their tokens.
                from app.auth.models import User
                from app.notifications.models import DeviceToken
                from beanie.odm.operators.find.comparison import In

                users = await User.find({"role": target_role}).to_list()
                user_ids = [str(u.id) for u in users]

                if not user_ids:
                    logger.info(f"No users found with role '{target_role}' for broadcast.")
                    return

                # Batch lookup of tokens for the filtered user IDs
                devices = await DeviceToken.find(
                    In(DeviceToken.user_id, user_ids),
                    DeviceToken.is_active == True,  # noqa: E712
                ).to_list()
                tokens = [d.token for d in devices]
            else:
                tokens = await notification_repository.get_all_active_tokens()

            if not tokens:
                return

            # FCM limits multicast to 500 tokens per call.
            batch_size = 500
            for i in range(0, len(tokens), batch_size):
                batch_tokens = tokens[i:i + batch_size]
                await self._send_with_retry(batch_tokens, title, body, None)
                
        except Exception as e:
            logger.error(f"Error processing broadcast: {e}")

    async def _send_with_retry(self, tokens: List[str], title: str, body: str, data: Dict[str, Any], max_retries: int = 3):
        """Sends a multicast message with retry logic and cleans up bad tokens."""
        for attempt in range(max_retries):
            success, failure, failed_tokens = fcm_client.send_multicast(tokens, title, body, data)
            
            if failure > 0 and failed_tokens:
                # Clean up unregistered tokens immediately
                for token in failed_tokens:
                    await notification_repository.deactivate_token(token)
                    
                # If there are failures, maybe retry for server-errors?
                # Usually FCM returns failure for invalid tokens which we shouldn't retry.
                # If it's a 500 error from FCM, it's different.
                # For this implementation, we just remove bad tokens and stop retrying.
                # In a robust system, we check the exact exception.
                break 
                
            if success > 0 or attempt == max_retries - 1:
                break
                
            # Exponential backoff
            await asyncio.sleep(2 ** attempt)

    def _is_allowed_by_preferences(self, notif_type: str, prefs: NotificationPreference) -> bool:
        """Check if the notification type is enabled in the user's preferences."""
        from .templates import NotificationType
        import datetime as dt

        # --- Quiet Hours Enforcement ---
        if prefs.quiet_hours_enabled and prefs.quiet_hours_start and prefs.quiet_hours_end:
            try:
                now_time = dt.datetime.now().strftime("%H:%M")
                # Compare strings directly (HH:MM format sorts lexicographically)
                start = prefs.quiet_hours_start
                end = prefs.quiet_hours_end

                # Handle overnight quiet hours (e.g., 22:00 – 07:00)
                if start <= end:
                    in_quiet_hours = start <= now_time <= end
                else:
                    in_quiet_hours = now_time >= start or now_time <= end

                # Only suppress non-critical notification types during quiet hours
                non_critical = notif_type not in [
                    NotificationType.ADMIN_BROADCAST,
                    NotificationType.SYSTEM_ANNOUNCEMENT,
                ]
                if in_quiet_hours and non_critical:
                    logger.info(f"Notification '{notif_type}' suppressed during quiet hours.")
                    return False
            except Exception:
                pass  # If quiet hours check fails, allow through

        # --- Category Preferences ---
        if notif_type in [NotificationType.BOOKING_CREATED, NotificationType.BOOKING_ACCEPTED,
                          NotificationType.BOOKING_ASSIGNED, NotificationType.BOOKING_CANCELLED,
                          NotificationType.BOOKING_COMPLETED]:
            return prefs.booking_notifications
            
        if notif_type in [NotificationType.QUOTATION_RECEIVED, NotificationType.QUOTATION_ACCEPTED, NotificationType.QUOTATION_REJECTED]:
            return prefs.booking_notifications  # Grouped under booking notifications
            
        if notif_type in [NotificationType.WORKER_ARRIVING, NotificationType.WORKER_REACHED]:
            return prefs.booking_notifications
            
        if notif_type == NotificationType.AI_RECOMMENDATION:
            return prefs.ai_notifications
            
        # Admin broadcasts and system announcements cannot be disabled
        if notif_type in [NotificationType.ADMIN_BROADCAST, NotificationType.SYSTEM_ANNOUNCEMENT]:
            return True
            
        # By default, allow
        return True

    # --- History Management ---
    
    async def get_history(self, user_id: str, skip: int = 0, limit: int = 50):
        return await notification_repository.get_user_notifications(user_id, skip, limit)
        
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        return await notification_repository.mark_as_read(notification_id, user_id)

    async def mark_all_as_read(self, user_id: str) -> int:
        return await notification_repository.mark_all_as_read(user_id)

    async def delete_notification(self, notification_id: str, user_id: str) -> bool:
        return await notification_repository.delete_notification(notification_id, user_id)

    async def delete_all_read(self, user_id: str) -> int:
        return await notification_repository.delete_all_read(user_id)

    async def get_unread_count(self, user_id: str) -> int:
        return await notification_repository.get_unread_count(user_id)

notification_service = NotificationService()
