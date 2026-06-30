"""AIOS API v1 Router."""

from fastapi import APIRouter

from aios.api.v1 import (
    agents,
    knowledge,
    memory,
    plugins,
    projects,
    providers,
    security,
    system,
    workflows,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(system.router, tags=["system"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
api_router.include_router(providers.router, prefix="/providers", tags=["providers"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
