import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import beanie
from app.auth.models import User
from app.booking.models import Booking
from app.quotation.models import Quotation, QuotationHistory
from app.application.models import JobApplication
from app.notifications.models import Notification, NotificationPreference, DeviceToken
from app.notifications.service import notification_service
from app.notifications.templates import NotificationType

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    await beanie.init_beanie(database=client.ally, document_models=[User, Booking, JobApplication, Quotation, QuotationHistory, Notification, NotificationPreference, DeviceToken])
    
    # Existing quotation
    quot = await Quotation.get("6a74daf81b3dd2a3e009e003")
    booking = await Booking.get(quot.booking_id)
    
    print(f"Customer ID: {booking.customer_id}")
    print(f"Amount: {quot.total_amount}")
    
    try:
        await notification_service._process_single_notification(
            user_id=str(booking.customer_id),
            notif_type=NotificationType.QUOTATION_RECEIVED,
            data={
                "booking_id": str(booking.id),
                "quotation_id": str(quot.id),
                "amount": f"₹{quot.total_amount:,.0f}",
                "booking_number": booking.booking_number,
            },
        )
        print("Success calling _process_single_notification")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
