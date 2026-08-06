import asyncio
import httpx
from datetime import datetime, timedelta, timezone
from jose import jwt

# Copy settings from config
SECRET_KEY = "dummy-secret-key-for-local-dev-only"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def main():
    # Worker token
    worker_id = "6a737724c250dcf3b6bb246e"
    token = create_access_token({"sub": worker_id})
    headers = {"Authorization": f"Bearer {token}"}
    
    # We need a fresh pending booking to test. Let's create one directly in the DB or just hit a booking endpoint if we have one.
    # Actually, we can just test update_quotation on a draft!
    
if __name__ == '__main__':
    asyncio.run(main())
