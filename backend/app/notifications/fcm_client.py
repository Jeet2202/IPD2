import os
import logging
from typing import List, Dict, Any, Tuple
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FCMClient:
    def __init__(self):
        self.app = None
        self.is_initialized = False
        self._initialize()

    def _initialize(self):
        if self.is_initialized:
            return

        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if not cred_path:
            logger.warning("FIREBASE_CREDENTIALS_PATH not set. FCM will not be initialized.")
            return

        # Handle absolute or relative paths
        if not os.path.isabs(cred_path):
            # Assume relative to the backend root (where main.py is executed)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cred_path = os.path.join(base_dir, cred_path)

        if not os.path.exists(cred_path):
            logger.error(f"Firebase credentials file not found at {cred_path}")
            return

        try:
            cred = credentials.Certificate(cred_path)
            # Check if default app is already initialized to avoid ValueError
            if not firebase_admin._apps:
                self.app = firebase_admin.initialize_app(cred)
            else:
                self.app = firebase_admin.get_app()
            
            self.is_initialized = True
            logger.info("Firebase Admin SDK successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")

    def send_multicast(self, tokens: List[str], title: str, body: str, data: Dict[str, Any] = None) -> Tuple[int, int, List[str]]:
        """
        Send a message to multiple devices.
        Returns: (success_count, failure_count, failed_tokens_list)
        """
        if not self.is_initialized or not tokens:
            return 0, len(tokens), tokens

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=self._sanitize_data(data),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='ally_high_importance_channel',
                    sound='default'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True
                    )
                )
            ),
            tokens=tokens,
        )

        try:
            response = messaging.send_each_for_multicast(message)
            
            # Identify failed tokens
            failed_tokens = []
            if response.failure_count > 0:
                for idx, resp in enumerate(response.responses):
                    if not resp.success:
                        # Common errors indicating an invalid/expired token:
                        # messaging.UnregisteredError, InvalidRegistrationError
                        failed_tokens.append(tokens[idx])
                        logger.warning(f"FCM send failed for token {tokens[idx]}: {resp.exception}")

            return response.success_count, response.failure_count, failed_tokens

        except Exception as e:
            logger.error(f"FCM multicast send error: {e}")
            return 0, len(tokens), tokens

    def send_single(self, token: str, title: str, body: str, data: Dict[str, Any] = None) -> bool:
        """
        Send a message to a single device.
        Returns True if successful, False if failed.
        """
        if not self.is_initialized or not token:
            return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=self._sanitize_data(data),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='ally_high_importance_channel',
                    sound='default'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        content_available=True
                    )
                )
            ),
            token=token,
        )

        try:
            messaging.send(message)
            return True
        except messaging.UnregisteredError:
            logger.warning(f"FCM token unregistered: {token}")
            return False
        except Exception as e:
            logger.error(f"FCM single send error: {e}")
            return False

    def _sanitize_data(self, data: Dict[str, Any] = None) -> Dict[str, str]:
        """FCM data payload strictly requires string values for all keys."""
        if not data:
            return {}
        return {str(k): str(v) for k, v in data.items()}

fcm_client = FCMClient()
