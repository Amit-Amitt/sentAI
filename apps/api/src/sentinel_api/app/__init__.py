from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from sentinel_api.api.routers.health import router as health_router
from sentinel_api.config.settings import settings
from sentinel_api.exceptions.handlers import register_exception_handlers
from sentinel_api.logging.logger import setup_logging
from sentinel_api.middleware import (
    LoggingMiddleware,
    ProcessTimeMiddleware,
    RequestIdMiddleware,
)

logger = structlog.get_logger("sentinel_api.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log startup events
    logger.info(
        "Sentinel AI Backend API starting up",
        environment=settings.APP_ENV,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )
    
    # Initialize DB schemas automatically
    from sentinel_api.database.base import Base
    from sentinel_api.database.session import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield

    # Log shutdown events
    logger.info("Sentinel AI Backend API shutting down")


def create_app() -> FastAPI:
    # Set up structured logging configurations
    setup_logging()

    app = FastAPI(
        title="Sentinel AI API",
        description="The Autonomous AI Incident Commander Backend API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configured Trusted Host middleware (protection against Host header attacks)
    # Allow localhost, common local loopback IPs, and wildcards/specific hosts
    # in production.
    allowed_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "test"]
    if settings.is_prod or settings.is_test:
        allowed_hosts = [
            "*"
        ]  # In production or testing, replace with domain or explicit settings
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount custom middlewares
    # Note: Middlewares execute in reverse order of addition.
    # RequestIdMiddleware (runs 1st) -> LoggingMiddleware (runs 2nd) ->
    # ProcessTimeMiddleware (runs 3rd).
    app.add_middleware(ProcessTimeMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Register global exception translation layer
    register_exception_handlers(app)

    # Wire API endpoints
    from sentinel_api.api.v1.routers import api_router as api_v1_router
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()
