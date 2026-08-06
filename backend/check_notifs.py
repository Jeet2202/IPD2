import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    db = client['ally']
    notifs = await db['notifications'].find().sort('_id', -1).limit(5).to_list(5)
    for n in notifs:
        print(str(n).encode('utf-8'))

if __name__ == '__main__':
    asyncio.run(main())
