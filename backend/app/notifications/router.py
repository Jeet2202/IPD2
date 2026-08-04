from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from typing import Any

from app.auth.models import User
from app.api.dependencies.auth import get_current_user, get_current_admin
from .schemas import (
    DeviceTokenRequest, DeviceTokenUpdate, DeviceTokenRemove,
    NotificationListResponse, NotificationResponse,
    PreferencesUpdate, PreferencesResponse,
    SendNotificationRequest, BroadcastRequest
)
from .service import notification_service

router = APIRouter()

# --- Device Management ---

@router.post("/register-device", summary="Register a device token for push notifications")
async def register_device(
    payload: DeviceTokenRequest,
    current_user: User = Depends(get_current_user)
) -> dict:
    await notification_service.register_device(str(current_user.id), payload.token, payload.platform)
    return {"message": "Device token registered successfully"}

@router.put("/update-device", summary="Update an existing device token")
async def update_device(
    payload: DeviceTokenUpdate,
    current_user: User = Depends(get_current_user)
) -> dict:
    await notification_service.update_device(str(current_user.id), payload.old_token, payload.new_token)
    return {"message": "Device token updated successfully"}

@router.delete("/remove-device", summary="Remove a device token")
async def remove_device(
    payload: DeviceTokenRemove,
    current_user: User = Depends(get_current_user)
) -> dict:
    await notification_service.remove_device(payload.token)
    return {"message": "Device token removed successfully"}


# --- Notification History ---

@router.get("", response_model=NotificationListResponse, summary="Get notification history")
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
) -> Any:
    items, total = await notification_service.get_history(str(current_user.id), skip, limit)
    
    # Map to response schema
    mapped_items = [
        NotificationResponse(
            id=str(item.id),
            title=item.title,
            body=item.body,
            type=item.type,
            data=item.data,
            is_read=item.is_read,
            created_at=item.created_at
        )
        for item in items
    ]
    
    return NotificationListResponse(total=total, items=mapped_items)

@router.put("/read/{id}", summary="Mark a notification as read")
async def mark_as_read(
    id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    success = await notification_service.mark_as_read(id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.put("/read-all", summary="Mark all notifications as read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user)
) -> dict:
    count = await notification_service.mark_all_as_read(str(current_user.id))
    return {"message": f"{count} notifications marked as read"}

@router.delete("/read-all", summary="Delete all read notifications")
async def delete_all_read(
    current_user: User = Depends(get_current_user)
) -> dict:
    count = await notification_service.delete_all_read(str(current_user.id))
    return {"message": f"{count} read notifications deleted"}

@router.delete("/{id}", summary="Delete a notification")
async def delete_notification(
    id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    success = await notification_service.delete_notification(id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"message": "Notification deleted"}

@router.get("/unread-count", summary="Get unread notification count")
async def get_unread_count(
    current_user: User = Depends(get_current_user)
) -> dict:
    count = await notification_service.get_unread_count(str(current_user.id))
    return {"count": count}


# --- Preferences ---

@router.get("/preferences", response_model=PreferencesResponse, summary="Get notification preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user)
) -> Any:
    return await notification_service.get_preferences(str(current_user.id))

@router.put("/preferences", response_model=PreferencesResponse, summary="Update notification preferences")
async def update_preferences(
    payload: PreferencesUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    update_data = payload.model_dump(exclude_unset=True)
    return await notification_service.update_preferences(str(current_user.id), update_data)


# --- Admin Endpoints ---

@router.post("/send", summary="Send a notification to a specific user (Admin Only)")
async def send_notification(
    payload: SendNotificationRequest,
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin)
) -> dict:
    """
    Queue a notification for a specific user.
    """
    notification_service.queue_notification(
        background_tasks,
        user_id=payload.user_id,
        notif_type=payload.type,
        data=payload.data or {"title": payload.title, "body": payload.body}
    )
    return {"message": "Notification queued successfully"}

@router.post("/broadcast", summary="Broadcast a notification (Admin Only)")
async def broadcast_notification(
    payload: BroadcastRequest,
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin)
) -> dict:
    """
    Queue a broadcast notification to all users or a specific role.
    """
    notification_service.queue_broadcast(
        background_tasks,
        title=payload.title,
        body=payload.body,
        target_role=payload.target_role
    )
    return {"message": "Broadcast queued successfully"}
