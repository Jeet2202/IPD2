import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient('mongodb+srv://yourally2026_db_user:BBXoVJRFiK1LPVOo@cluster0.qxwcjiv.mongodb.net/?appName=Cluster0')
    db = client['ally']
    quotation_id = "6a74e0fbd026575956246c87"
    
    # fetch all history for this quotation
    from bson import ObjectId
    histories = await db['quotation_history'].find({"quotation_id": ObjectId(quotation_id)}).to_list(10)
    for h in histories:
        print(f"History Event: {h.get('event_type')} - {h.get('created_at')}")

if __name__ == '__main__':
    asyncio.run(main())
