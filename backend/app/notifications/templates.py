from enum import Enum
from typing import Tuple, Dict, Any

class NotificationType(str, Enum):
    BOOKING_CREATED = "Booking Created"
    BOOKING_ACCEPTED = "Booking Accepted"
    BOOKING_ASSIGNED = "Booking Assigned"
    BOOKING_CANCELLED = "Booking Cancelled"
    BOOKING_COMPLETED = "Booking Completed"
    QUOTATION_RECEIVED = "Quotation Received"
    QUOTATION_ACCEPTED = "Quotation Accepted"
    QUOTATION_REJECTED = "Quotation Rejected"
    WORKER_ARRIVING = "Worker Arriving"
    WORKER_REACHED = "Worker Reached"
    AI_RECOMMENDATION = "AI Recommendation Ready"
    ADMIN_BROADCAST = "Admin Broadcast"
    SYSTEM_ANNOUNCEMENT = "System Announcement"

def get_notification_template(notif_type: str, data: Dict[str, Any] = None) -> Tuple[str, str]:
    """
    Returns (title, body) based on the notification type and context data.
    """
    data = data or {}
    
    if notif_type == NotificationType.BOOKING_CREATED:
        return "New Booking Request", f"You have received a new booking request for {data.get('service_name', 'a service')}."
    elif notif_type == NotificationType.BOOKING_ACCEPTED:
        return "Booking Accepted", f"Your booking for {data.get('service_name', 'a service')} has been accepted."
    elif notif_type == NotificationType.BOOKING_ASSIGNED:
        worker = data.get("worker_name", "A worker")
        return "Worker Assigned", f"{worker} has been assigned to your booking."
    elif notif_type == NotificationType.BOOKING_CANCELLED:
        return "Booking Cancelled", f"The booking {data.get('booking_id', '')} was cancelled."
    elif notif_type == NotificationType.BOOKING_COMPLETED:
        return "Booking Completed", f"Your booking for {data.get('service_name', 'a service')} is complete."
    elif notif_type == NotificationType.QUOTATION_RECEIVED:
        return "New Quotation", f"You received a quotation of {data.get('amount', '')} for your request."
    elif notif_type == NotificationType.QUOTATION_ACCEPTED:
        return "Quotation Accepted", "The customer has accepted your quotation."
    elif notif_type == NotificationType.QUOTATION_REJECTED:
        return "Quotation Rejected", "Your quotation was rejected by the customer."
    elif notif_type == NotificationType.WORKER_ARRIVING:
        return "Worker is Arriving", f"{data.get('worker_name', 'Your worker')} is on the way!"
    elif notif_type == NotificationType.WORKER_REACHED:
        return "Worker Reached", f"{data.get('worker_name', 'Your worker')} has reached the location."
    elif notif_type == NotificationType.AI_RECOMMENDATION:
        return "AI Recommendation", "Your personalized service recommendations are ready."
    elif notif_type == NotificationType.ADMIN_BROADCAST:
        return data.get("title", "Admin Broadcast"), data.get("body", "Important information from Ally.")
    elif notif_type == NotificationType.SYSTEM_ANNOUNCEMENT:
        return data.get("title", "System Update"), data.get("body", "There is a system update.")
    else:
        # Fallback for custom or unknown types
        return data.get("title", "Notification"), data.get("body", "You have a new notification.")
