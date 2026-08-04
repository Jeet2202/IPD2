import socketio
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize message queue manager if configured (for horizontal scaling)
client_manager = None
if settings.SOCKET_MESSAGE_QUEUE:
    try:
        client_manager = socketio.AsyncRedisManager(settings.SOCKET_MESSAGE_QUEUE)
        logger.info(f"Initialized AsyncRedisManager with {settings.SOCKET_MESSAGE_QUEUE}")
    except Exception as e:
        logger.error(f"Failed to initialize AsyncRedisManager: {e}")
        # Fall back to default in-memory manager

# Initialize Socket.IO AsyncServer
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.SOCKET_CORS_ALLOWED_ORIGINS,
    client_manager=client_manager,
    logger=settings.DEBUG,
    engineio_logger=settings.DEBUG,
)

# Create the ASGI application wrapping the Socket.IO server
# By setting socketio_path='', we can cleanly mount it in FastAPI via app.mount('/socket.io', socket_app)
socket_app = socketio.ASGIApp(sio, socketio_path='')

logger.info("Socket.IO server initialized.")
