"""AIOS Lifecycle Events."""

import structlog
from typing import Callable, Awaitable
from fastapi import FastAPI

logger = structlog.get_logger(__name__)

# Type alias for lifecycle handlers
LifecycleHandler = Callable[[], Awaitable[None]]


async def create_start_app_handler(app: FastAPI) -> LifecycleHandler:
    """Create startup event handler."""
    async def start_app() -> None:
        logger.info("Starting AIOS services...")
        
        # Initialize database
        try:
            from aios.database.connection import init_db
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
        
        # Initialize vector store
        try:
            from aios.memory.vector import init_vector_store
            await init_vector_store()
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error("Failed to initialize vector store", error=str(e))
        
        # Initialize graph store
        try:
            from aios.memory.graph import init_graph_store
            await init_graph_store()
            logger.info("Graph store initialized")
        except Exception as e:
            logger.error("Failed to initialize graph store", error=str(e))
        
        logger.info("AIOS services started successfully")
    
    return start_app


async def create_stop_app_handler(app: FastAPI) -> LifecycleHandler:
    """Create shutdown event handler."""
    async def stop_app() -> None:
        logger.info("Shutting down AIOS services...")
        
        # Close database connections
        try:
            from aios.database.connection import close_db
            await close_db()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Failed to close database", error=str(e))
        
        logger.info("AIOS services stopped")
    
    return stop_app
