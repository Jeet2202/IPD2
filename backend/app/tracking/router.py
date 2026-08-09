from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user, get_current_worker
from app.auth.models import User
from app.booking.service import BookingService
from app.tracking.schemas import LocationUpdatePayload, TrackingStateResponse
from app.booking.repository import BookingRepository
from app.core.exceptions import NotFoundException, ForbiddenException
from app.sockets.server import sio
from app.sockets.room_manager import room_manager

router = APIRouter(prefix="/tracking", tags=["Live Tracking"])

@router.post("/location", response_model=dict)
async def update_worker_location(
    payload: LocationUpdatePayload,
    current_worker: User = Depends(get_current_worker)
):
    """Worker posts their current location."""
    await BookingService.update_worker_location(
        worker_user=current_worker,
        booking_id=payload.booking_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    
    # Emit to Socket.IO room
    await sio.emit(
        "worker_location_updated",
        {
            "booking_id": payload.booking_id,
            "worker_id": str(current_worker.id),
            "lat": payload.latitude,
            "lng": payload.longitude,
            "timestamp": payload.timestamp.isoformat()
        },
        room=room_manager.get_booking_room(payload.booking_id)
    )
    
    return {"status": "success"}

@router.get("/{booking_id}", response_model=TrackingStateResponse)
async def get_tracking_state(
    booking_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Customer (or worker) fetches the latest tracking state."""
    booking = await BookingRepository.get_by_id(booking_id)
    if not booking:
        raise NotFoundException("Booking not found")
        
    if current_user.role == "customer" and str(booking.customer_id) != str(current_user.id):
        raise ForbiddenException("You cannot view tracking for this booking")
        
    if current_user.role == "worker" and str(booking.worker_id) != str(current_user.id):
        raise ForbiddenException("You cannot view tracking for this booking")
        
    loc = booking.tracking.worker_location
    return TrackingStateResponse(
        is_active=booking.tracking.is_active,
        worker_location={"latitude": loc.latitude, "longitude": loc.longitude} if loc else None,
        last_updated_at=booking.tracking.last_updated_at
    )
