"""AIOS Provider Endpoints."""

import structlog
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now
_providers: dict = {}


@router.get("")
async def list_providers() -> List[dict]:
    """List all configured providers."""
    return list(_providers.values())


@router.post("/configure", status_code=201)
async def configure_provider(provider: dict) -> dict:
    """Configure a provider."""
    import uuid
    from datetime import datetime
    
    provider_id = str(uuid.uuid4())
    provider_data = {
        "id": provider_id,
        "name": provider.get("name"),
        "type": provider.get("type"),
        "base_url": provider.get("base_url"),
        "api_key": provider.get("api_key"),
        "models": provider.get("models", []),
        "status": "configured",
        "configured_at": datetime.utcnow().isoformat(),
    }
    _providers[provider_id] = provider_data
    logger.info("Provider configured", provider_id=provider_id, name=provider.get("name"))
    return provider_data


@router.get("/{provider_id}")
async def get_provider(provider_id: str) -> dict:
    """Get a provider by ID."""
    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    return _providers[provider_id]


@router.post("/{provider_id}/test")
async def test_provider(provider_id: str) -> dict:
    """Test a provider connection."""
    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Placeholder for actual provider test
    return {
        "provider_id": provider_id,
        "status": "ok",
        "latency_ms": 0,
        "message": "Provider test not yet implemented",
    }


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(provider_id: str) -> None:
    """Delete a provider configuration."""
    if provider_id not in _providers:
        raise HTTPException(status_code=404, detail="Provider not found")
    del _providers[provider_id]
    logger.info("Provider deleted", provider_id=provider_id)
