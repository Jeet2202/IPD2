import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import beanie
from app.auth.models import User
from app.booking.models import Booking
from app.application.models import JobApplication
from app.quotation.models import Quotation, QuotationHistory
from app.quotation.service import QuotationService
from app.quotation.schemas import QuotationCreateRequest
from app.notifications.models import Notification, NotificationPreference, DeviceToken

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    await beanie.init_beanie(database=client.ally, document_models=[User, Booking, JobApplication, Quotation, QuotationHistory, Notification, NotificationPreference, DeviceToken])
    
    worker = await User.find_one({"_id": beanie.PydanticObjectId("6a737724c250dcf3b6bb246e")})
    booking = await Booking.find_one({"_id": beanie.PydanticObjectId("6a74dadfef3224de2a4b3250")})
    
    svc = QuotationService()
    payload = QuotationCreateRequest(
        booking_id=str(booking.id),
        application_id="6a74daed1b3dd2a3e009e002",
        labour_cost=100.0,
        material_cost=0.0,
        estimated_duration="2 days",
        validity_date="2026-08-21",
        is_draft=False
    )
    
    try:
        res = await svc.create_quotation(worker, payload)
        print(f"Success! Quotation ID: {res.id}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
