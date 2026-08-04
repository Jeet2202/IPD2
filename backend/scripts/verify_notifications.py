import asyncio
import sys
import os

# Ensure the app module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.notifications.fcm_client import fcm_client
from app.notifications.templates import get_notification_template, NotificationType
from app.core.config import settings

def verify():
    print("=== Push Notification Infrastructure Verification ===")
    
    # 1. Check FCM Initialization
    if fcm_client.is_initialized:
        print("[SUCCESS] Firebase Admin SDK initialized.")
    else:
        print("[WARNING] Firebase Admin SDK NOT initialized.")
        print("          Ensure 'firebase-credentials.json' exists at the path specified in .env")
        print(f"          Current FIREBASE_CREDENTIALS_PATH: {settings.FIREBASE_CREDENTIALS_PATH}")
        
    # 2. Test Templates
    title, body = get_notification_template(NotificationType.BOOKING_CREATED, {"service_name": "AC Repair"})
    print(f"\n[INFO] Generated Template for {NotificationType.BOOKING_CREATED}:")
    print(f"       Title: {title}")
    print(f"       Body:  {body}")
    
    # 3. Dummy Send (will fail but tests logic)
    print("\n[INFO] Attempting to send to a dummy token...")
    success = fcm_client.send_single("dummy_token_123", title, body)
    if not success:
        print("[SUCCESS] FCM Client correctly rejected/handled the dummy token.")
    else:
        print("[WARNING] FCM Client returned true for a dummy token (unexpected).")
        
    print("\nVerification script completed. To test real push notifications, connect a Flutter/React client to the backend.")

if __name__ == "__main__":
    verify()
