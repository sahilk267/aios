"""AIOS System Endpoints."""

import structlog
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends

from aios.core.config import Settings, settings

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status."""
    services: Dict[str, Any] = {}
    
    # Check database
    try:
        from aios.database.connection import check_db_health
        db_healthy = await check_db_health()
        services["database"] = {"status": "healthy" if db_healthy else "unhealthy"}
    except Exception as e:
        services["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Check vector store
    try:
        from aios.memory.vector import check_vector_store_health
        vector_healthy = await check_vector_store_health()
        services["vector_store"] = {"status": "healthy" if vector_healthy else "unhealthy"}
    except Exception as e:
        services["vector_store"] = {"status": "unhealthy", "error": str(e)}
    
    # Check graph store
    try:
        from aios.memory.graph import check_graph_store_health
        graph_healthy = await check_graph_store_health()
        services["graph_store"] = {"status": "healthy" if graph_healthy else "unhealthy"}
    except Exception as e:
        services["graph_store"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(
        s.get("status") == "healthy"
        for s in services.values()
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "services": services,
    }


@router.get("/info")
async def system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "features": {
            "agents": True,
            "workflows": True,
            "memory": True,
            "knowledge": True,
            "plugins": True,
            "providers": True,
        },
    }
