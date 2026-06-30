"""AIOS FastAPI Application Entry Point."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aios.api.v1.router import api_router
from aios.api.websocket.router import ws_router
from aios.core.config import settings
from aios.core.events import create_start_app_handler, create_stop_app_handler

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("AIOS starting up", version="0.1.0", env=settings.environment)
    start_handler = await create_start_app_handler(app)
    await start_handler()

    yield

    # Shutdown
    logger.info("AIOS shutting down")
    stop_handler = await create_stop_app_handler(app)
    await stop_handler()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AIOS",
        description="Artificial Intelligence Operating System",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router, prefix="/api/v1")

    # Include WebSocket routes
    app.include_router(ws_router, prefix="/ws")

    return app


app = create_application()


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "name": "AIOS",
        "version": "0.1.0",
        "description": "Artificial Intelligence Operating System",
        "docs": "/docs",
    }
