"""AIOS Provider Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProviderBase(BaseModel):
    """Base provider schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    models: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)


class ProviderCreate(ProviderBase):
    """Provider creation schema."""
    pass


class ProviderResponse(ProviderBase):
    """Provider response schema."""
    id: str
    status: str
    configured_at: str

    class Config:
        from_attributes = True


class ProviderTest(BaseModel):
    """Provider test response schema."""
    provider_id: str
    status: str
    latency_ms: float
    message: str
