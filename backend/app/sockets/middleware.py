import logging
from typing import Dict, Any, Tuple
import jwt
from app.core.config import settings

logger = logging.getLogger(__name__)

async def authenticate_socket(environ: Dict[str, Any], auth: Any) -> Tuple[bool, str, dict]:
    """
    Authenticate a socket connection using JWT token.
    The token can be in the `auth` dictionary (e.g., auth={"token": "..."})
    or in the headers (Authorization: Bearer ...).
    
    Returns:
        (is_authenticated, user_id, error_message)
    """
    token = None
    
    # Check auth dict first
    if isinstance(auth, dict) and "token" in auth:
        token = auth["token"]
        
    # Check headers if not in auth
    if not token and "HTTP_AUTHORIZATION" in environ:
        auth_header = environ["HTTP_AUTHORIZATION"]
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        logger.warning("Socket connection rejected: No authentication token provided.")
        return False, "", "No authentication token provided"

    try:
        if not settings.JWT_SECRET_KEY:
            # Fallback for development if not strict
            if not settings.is_production:
                logger.warning("JWT_SECRET_KEY not set. Allowing connection in non-production.")
                return True, "dev_user", {}

            return False, "", "Server configuration error"

        secret = settings.JWT_SECRET_KEY.get_secret_value()
        
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        user_id = payload.get("sub")
        
        if not user_id:
            return False, "", "Invalid token payload"
            
        return True, user_id, payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Socket connection rejected: Token has expired.")
        return False, "", "Token has expired"
    except jwt.InvalidTokenError as e:
        logger.warning(f"Socket connection rejected: Invalid token - {str(e)}")
        return False, "", "Invalid authentication token"
    except Exception as e:
        logger.error(f"Socket connection error during auth: {str(e)}")
        return False, "", "Authentication failed"
