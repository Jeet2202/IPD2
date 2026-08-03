from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import Database
from app.core.logging import logger
from app.core.exceptions import register_exception_handlers
from app.middleware.main_middleware import RequestLoggingMiddleware
from app.api.infrastructure import router as infra_router
from app.api.recommendations import router as rec_router
from app.api.search import router as search_router
from app.api.pricing import router as pricing_router
from app.assistant.api.assistant_router import router as assistant_router
from app.api.analytics import router as analytics_router
from app.utils.backend_client import BackendClient
from app.utils.model_loader import ModelLoader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Events
    logger.info("Starting up KaamSetu AI Service...")
    await Database.connect_db()
    
    yield
    
    # Shutdown Events
    logger.info("Shutting down KaamSetu AI Service...")
    await Database.close_db()
    await BackendClient.close()
    ModelLoader.clear_cache()

def create_app() -> FastAPI:
    app = FastAPI(
        title="KaamSetu AI Service",
        description="AI Microservice — Recommendations, Search, Pricing, AI Assistants",
        version="2.0.0",
        lifespan=lifespan
    )

    # Middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    register_exception_handlers(app)

    # Routers
    app.include_router(infra_router)
    app.include_router(rec_router)
    app.include_router(search_router)
    app.include_router(pricing_router)
    app.include_router(assistant_router)
    app.include_router(analytics_router)

    return app

app = create_app()
