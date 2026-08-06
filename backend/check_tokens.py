import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    db = client['ally']
    customer_id = '6a74ccb73df7e74ee3bd8280'
    tokens = await db['device_tokens'].find({"user_id": customer_id}).to_list(10)
    print(f"Customer tokens: {tokens}")

if __name__ == '__main__':
    asyncio.run(main())
