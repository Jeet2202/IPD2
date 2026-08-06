import asyncio
from app.notifications.repository import notification_repository
from app.notifications.templates import NotificationType
from app.notifications.service import notification_service
from motor.motor_asyncio import AsyncIOMotorClient
import beanie
from app.notifications.models import Notification, NotificationPreference, DeviceToken

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    await beanie.init_beanie(database=client.ally, document_models=[Notification, NotificationPreference, DeviceToken])
    try:
        await notification_service._process_single_notification(
            user_id="6a737724c250dcf3b6bb246e",
            notif_type=NotificationType.QUOTATION_RECEIVED,
            data={"amount": "₹1,000"}
        )
        print("Success")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())
