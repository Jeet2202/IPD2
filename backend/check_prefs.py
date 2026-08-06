import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    db = client['ally']
    # recent quotation
    q = await db['quotations'].find_one({"_id": "6a74daf81b3dd2a3e009e003"}) # wait, ObjectId!
    # better to just fetch the last quotation's booking_id
    q = await db['quotations'].find_one(sort=[('_id', -1)])
    print(f"Quotation: {q}")
    b = await db['bookings'].find_one({"_id": q['booking_id']})
    print(f"Booking: {b}")
    customer_id = b['customer_id']
    prefs = await db['notification_preferences'].find_one({"user_id": str(customer_id)})
    print(f"Prefs: {prefs}")

if __name__ == '__main__':
    asyncio.run(main())
