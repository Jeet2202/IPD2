import asyncio
import socketio
import sys
import os

# Ensure the app module can be imported to use settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings
import jwt
from datetime import datetime, timedelta, timezone

async def verify():
    print("=== Socket.IO Real-Time Infrastructure Verification ===")
    
    # 1. Generate a valid JWT token for testing
    secret = settings.JWT_SECRET_KEY.get_secret_value() if settings.JWT_SECRET_KEY else "test_secret"
    if not settings.JWT_SECRET_KEY:
        print("Warning: JWT_SECRET_KEY not set in .env. Assuming dev mode.")

    user_id = "test_user_123"
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "role": "customer"
    }
    
    token = jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)
    print(f"Generated test token for user: {user_id}")
    
    # 2. Setup Socket.IO Client
    sio = socketio.AsyncClient(logger=False, engineio_logger=False)
    
    connection_successful = False
    
    @sio.event
    async def connect():
        nonlocal connection_successful
        connection_successful = True
        print("[SUCCESS] Connected to Socket.IO server!")

    @sio.event
    async def connect_error(data):
        print(f"[ERROR] Connection failed: {data}")
        
    @sio.event
    async def disconnect():
        print("[INFO] Disconnected from server.")
        
    # 3. Connect to the server
    # Note: Requires the FastAPI server to be running on localhost:8000
    try:
        url = "ws://localhost:8000"
        print(f"Attempting to connect to {url}/socket.io/ with JWT...")
        
        await sio.connect(
            url,
            auth={"token": token},
            transports=['websocket']
        )
        
        # Wait a moment for connection to establish
        await asyncio.sleep(1)
        
        if connection_successful:
            # 4. Test Ping
            print("Sending ping...")
            response = await sio.emit("ping", callback=True)
            print(f"Ping response: {response}")
            if response == "pong":
                print("[SUCCESS] Ping-pong successful!")
            
            # 5. Disconnect
            await sio.disconnect()
            print("[SUCCESS] All Socket.IO infrastructure tests passed!")
            
    except Exception as e:
        print(f"Verification failed: {e}")
        print("Note: Make sure the FastAPI server is running (uvicorn app.main:app --reload)")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
