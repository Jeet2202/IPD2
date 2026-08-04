import logging
import asyncio
import socketio
from typing import Dict, Any, Optional

from .server import sio
from .connection_manager import connection_manager
from .presence_manager import presence_manager
from .room_manager import room_manager
from .middleware import authenticate_socket

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory cache of authorized booking participants per sid.
# Format: { sid: set[booking_id] }
# This avoids a DB round-trip on every message event.
# Populated on join_booking / join_booking_tracking, cleared on disconnect.
# ---------------------------------------------------------------------------
_authorized_bookings: Dict[str, set] = {}


async def _is_booking_participant(sid: str, booking_id: str) -> bool:
    """
    Verify that the socket user is an authorized participant of the booking.
    Uses an in-memory cache populated at room-join time.
    Falls back to a DB lookup if the cache entry is missing.
    """
    # Cache hit — fastest path
    if sid in _authorized_bookings and booking_id in _authorized_bookings[sid]:
        return True

    # Cache miss — validate via DB
    try:
        session = await sio.get_session(sid)
        user_id = session.get("user_id")
        if not user_id:
            return False

        from app.booking.models import Booking
        booking = await Booking.get(booking_id)
        if not booking:
            return False

        is_participant = (
            str(booking.customer_id) == user_id
            or str(booking.worker_id) == user_id
        )

        if is_participant:
            # Populate cache
            if sid not in _authorized_bookings:
                _authorized_bookings[sid] = set()
            _authorized_bookings[sid].add(booking_id)

        return is_participant

    except Exception as e:
        logger.error(f"Authorization check failed for sid={sid}, booking={booking_id}: {e}")
        return False


@sio.on("connect")
async def on_connect(sid: str, environ: Dict[str, Any], auth: Any):
    """
    Handle new socket connections.
    Validates JWT token, registers connection, updates presence, and joins default rooms.
    """
    logger.info(f"Socket connecting: {sid}")
    
    # 1. Authenticate
    is_auth, user_id, payload = await authenticate_socket(environ, auth)
    
    if not is_auth:
        logger.warning(f"Connection {sid} rejected: Authentication failed.")
        raise socketio.exceptions.ConnectionRefusedError("Authentication failed")

    # Save session data (user_id) to the socket session
    await sio.save_session(sid, {"user_id": user_id})

    # 2. Register Connection
    connection_manager.connect(sid, user_id)
    
    # 3. Update Presence
    device_type = "web"  # Placeholder — can parse from User-Agent or auth payload
    presence_manager.set_online(user_id, device_type=device_type)

    # 4. Join Default User Room
    user_room = room_manager.get_user_room(user_id)
    sio.enter_room(sid, user_room)
    logger.debug(f"Socket {sid} joined room {user_room}")
    
    # 5. Join Admin room if user has admin role
    role = payload.get("role", "customer")
    if role == "admin":
        admin_room = room_manager.get_admin_room()
        sio.enter_room(sid, admin_room)
        logger.debug(f"Socket {sid} (admin) joined room {admin_room}")

    logger.info(f"Socket connected successfully: {sid} for user {user_id}")

@sio.on("disconnect")
async def on_disconnect(sid: str):
    """
    Handle socket disconnections.
    Unregisters connection, clears booking authorization cache, and updates presence.
    """
    logger.info(f"Socket disconnecting: {sid}")
    
    # Clear authorization cache for this sid
    _authorized_bookings.pop(sid, None)
    
    # Try to get session to identify user
    try:
        session = await sio.get_session(sid)
        user_id = session.get("user_id")
    except KeyError:
        user_id = None

    if not user_id:
        user_id = connection_manager.get_user_id(sid)

    if user_id:
        connection_manager.disconnect(sid)
        presence_manager.set_offline(user_id)
        logger.info(f"Socket disconnected successfully: {sid} for user {user_id}")
    else:
        logger.debug(f"Socket disconnected (unregistered): {sid}")

@sio.on("ping")
async def on_ping(sid: str):
    """
    Custom application-level ping for latency checking or keep-alive.
    """
    return "pong"

# --- Phase 7.3: Booking Session Communication ---

@sio.on("join_booking")
async def on_join_booking(sid: str, data: Dict[str, Any]):
    """
    Join a specific booking's chat room.
    Expects data: {"booking_id": "..."}
    Validates that the socket user is a participant of the booking.
    """
    booking_id = data.get("booking_id")
    if not booking_id:
        return {"error": "booking_id required"}

    if not await _is_booking_participant(sid, booking_id):
        logger.warning(f"Socket {sid} unauthorized join_booking attempt for {booking_id}")
        return {"error": "Not authorized for this booking"}
        
    chat_room = room_manager.get_chat_room(booking_id)
    sio.enter_room(sid, chat_room)
    logger.info(f"Socket {sid} joined chat room {chat_room}")
    return {"status": "joined", "room": chat_room}

@sio.on("leave_booking")
async def on_leave_booking(sid: str, data: Dict[str, Any]):
    """
    Leave a specific booking's chat room.
    """
    booking_id = data.get("booking_id")
    if booking_id:
        chat_room = room_manager.get_chat_room(booking_id)
        sio.leave_room(sid, chat_room)
        # Remove from authorization cache
        if sid in _authorized_bookings:
            _authorized_bookings[sid].discard(booking_id)
        logger.info(f"Socket {sid} left chat room {chat_room}")

@sio.on("send_message")
async def on_send_message(sid: str, data: Dict[str, Any]):
    """
    Broadcast a chat message to the booking room.
    Expects data: {"booking_id": "...", "message": "...", "sender_id": "..."}
    Optional media: {"media_url": "...", "media_type": "image"|"document"}
    """
    booking_id = data.get("booking_id")
    sender_id = data.get("sender_id")
    if not booking_id or not sender_id:
        return {"error": "booking_id and sender_id required"}

    # Authorization check
    if not await _is_booking_participant(sid, booking_id):
        logger.warning(f"Socket {sid} unauthorized send_message for booking {booking_id}")
        return {"error": "Not authorized for this booking"}
        
    chat_room = room_manager.get_chat_room(booking_id)
    
    # Broadcast to everyone else in the room
    await sio.emit("receive_message", data, room=chat_room, skip_sid=sid)
    logger.debug(f"Message broadcasted to {chat_room} by {sid}")

    # Optional: Media push notification — send via queue to avoid blocking
    media_type = data.get("media_type")
    if media_type:
        asyncio.create_task(_send_media_notification(booking_id, sender_id, media_type))

    return {"status": "delivered", "timestamp": data.get("timestamp")}


async def _send_media_notification(booking_id: str, sender_id: str, media_type: str):
    """
    Background task: send a push notification when a media message is sent.
    Isolated so that any failure does not affect message delivery.
    """
    try:
        from app.booking.models import Booking
        from app.notifications.service import notification_service
        from app.notifications.templates import NotificationType
        from fastapi import BackgroundTasks

        booking = await Booking.get(booking_id)
        if not booking:
            return

        is_customer_sender = (str(booking.customer_id) == sender_id)
        recipient_id = str(booking.worker_id) if is_customer_sender else str(booking.customer_id)
        if not recipient_id or recipient_id == "None":
            return

        sender_role = "Customer" if is_customer_sender else "Worker"
        media_noun = "an image" if media_type == "image" else "a document"

        # Use a temporary BackgroundTasks for the public queue_notification interface
        bg = BackgroundTasks()
        notification_service.queue_notification(
            bg,
            user_id=recipient_id,
            notif_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            data={
                "title": "New Media",
                "body": f"{sender_role} sent {media_noun}.",
                "booking_id": booking_id,
            },
        )
        # Execute the background task inline inside this async task
        await bg()

    except Exception as e:
        logger.error(f"Failed to send media push notification for booking {booking_id}: {e}")


@sio.on("typing_indicator")
async def on_typing_indicator(sid: str, data: Dict[str, Any]):
    """
    Broadcast typing status.
    Expects data: {"booking_id": "...", "is_typing": bool, "sender_id": "..."}
    """
    booking_id = data.get("booking_id")
    if booking_id:
        chat_room = room_manager.get_chat_room(booking_id)
        await sio.emit("typing_update", data, room=chat_room, skip_sid=sid)

@sio.on("read_receipt")
async def on_read_receipt(sid: str, data: Dict[str, Any]):
    """
    Broadcast read receipt for a message.
    Expects data: {"booking_id": "...", "message_id": "...", "reader_id": "..."}
    """
    booking_id = data.get("booking_id")
    if booking_id:
        chat_room = room_manager.get_chat_room(booking_id)
        await sio.emit("message_read", data, room=chat_room, skip_sid=sid)

# --- Phase 7.4: Live Booking Tracking ---

@sio.on("join_booking_tracking")
async def on_join_booking_tracking(sid: str, data: Dict[str, Any]):
    """
    Join a specific booking's tracking room for live status updates.
    Expects data: {"booking_id": "..."}
    Validates that the socket user is a participant of the booking.
    """
    booking_id = data.get("booking_id")
    if not booking_id:
        return {"error": "booking_id required"}

    if not await _is_booking_participant(sid, booking_id):
        logger.warning(f"Socket {sid} unauthorized join_booking_tracking for {booking_id}")
        return {"error": "Not authorized for this booking"}
        
    booking_room = room_manager.get_booking_room(booking_id)
    sio.enter_room(sid, booking_room)
    logger.info(f"Socket {sid} joined tracking room {booking_room}")
    return {"status": "joined", "room": booking_room}

@sio.on("leave_booking_tracking")
async def on_leave_booking_tracking(sid: str, data: Dict[str, Any]):
    """
    Leave a specific booking's tracking room.
    """
    booking_id = data.get("booking_id")
    if booking_id:
        booking_room = room_manager.get_booking_room(booking_id)
        sio.leave_room(sid, booking_room)
        logger.info(f"Socket {sid} left tracking room {booking_room}")

@sio.on("update_booking_status")
async def on_update_booking_status(sid: str, data: Dict[str, Any]):
    """
    Broadcast booking status update to the tracking room.
    Expects data: {"booking_id": "...", "status": "...", "timestamp": "..."}
    Only authorized booking participants may emit this event.
    """
    booking_id = data.get("booking_id")
    if not booking_id:
        return {"error": "booking_id required"}

    if not await _is_booking_participant(sid, booking_id):
        logger.warning(f"Socket {sid} unauthorized update_booking_status for {booking_id}")
        return {"error": "Not authorized for this booking"}
        
    booking_room = room_manager.get_booking_room(booking_id)
    await sio.emit("booking_status_updated", data, room=booking_room, skip_sid=sid)
    logger.debug(f"Booking status update broadcasted to {booking_room} by {sid}")
    return {"status": "broadcasted"}

@sio.on("update_worker_location")
async def on_update_worker_location(sid: str, data: Dict[str, Any]):
    """
    Broadcast live worker location to the tracking room.
    Expects data: {"booking_id": "...", "lat": ..., "lng": ..., "distance": ..., "eta": ..., "timestamp": ...}
    Only authorized booking participants (worker) may emit this event.
    """
    booking_id = data.get("booking_id")
    if not booking_id:
        return {"error": "booking_id required"}

    if not await _is_booking_participant(sid, booking_id):
        logger.warning(f"Socket {sid} unauthorized update_worker_location for {booking_id}")
        return {"error": "Not authorized for this booking"}
        
    booking_room = room_manager.get_booking_room(booking_id)
    await sio.emit("worker_location_updated", data, room=booking_room, skip_sid=sid)
    logger.debug(f"Worker location broadcasted to {booking_room} by {sid}")
    return {"status": "broadcasted"}
