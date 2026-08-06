import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    db = client['ally']
    # Find a pending booking
    b = await db['bookings'].find_one({"status": "pending"})
    print(f"Pending Booking: {b}")
    # Find a pending application
    app = await db['job_applications'].find_one({"status": "pending"})
    print(f"Pending Application: {app}")

if __name__ == '__main__':
    asyncio.run(main())
