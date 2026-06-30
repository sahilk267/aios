"""AIOS Plugin Endpoints."""


import structlog
from fastapi import APIRouter, HTTPException, Query

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now
_plugins: dict = {}


@router.get("")
async def list_plugins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plugin_type: str | None = None,
) -> list[dict]:
    """List all plugins."""
    plugins = list(_plugins.values())
    if plugin_type:
        plugins = [p for p in plugins if p.get("type") == plugin_type]
    return plugins[skip : skip + limit]


@router.post("/install", status_code=201)
async def install_plugin(plugin: dict) -> dict:
    """Install a plugin."""
    import uuid
    from datetime import datetime

    plugin_id = str(uuid.uuid4())
    plugin_data = {
        "id": plugin_id,
        "name": plugin.get("name"),
        "type": plugin.get("type"),
        "version": plugin.get("version", "0.1.0"),
        "status": "installed",
        "config": plugin.get("config", {}),
        "installed_at": datetime.utcnow().isoformat(),
    }
    _plugins[plugin_id] = plugin_data
    logger.info("Plugin installed", plugin_id=plugin_id, name=plugin.get("name"))
    return plugin_data


@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str) -> dict:
    """Get a plugin by ID."""
    if plugin_id not in _plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")
    return _plugins[plugin_id]


@router.delete("/{plugin_id}", status_code=204)
async def uninstall_plugin(plugin_id: str) -> None:
    """Uninstall a plugin."""
    if plugin_id not in _plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")
    del _plugins[plugin_id]
    logger.info("Plugin uninstalled", plugin_id=plugin_id)
