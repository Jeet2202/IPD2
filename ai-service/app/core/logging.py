import logging
import sys
from app.core.config import settings

def setup_logging():
    logging_level = getattr(logging, settings.LOGGING_LEVEL.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("ai_service")
    logger.setLevel(logging_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to handler
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Set the root logger
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[console_handler]
    )

    # Adjust third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging_level)
    logging.getLogger("motor").setLevel(logging.WARNING)

    return logger

logger = setup_logging()
