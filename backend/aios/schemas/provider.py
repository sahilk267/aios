"""AIOS Provider Schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ProviderBase(BaseModel):
    """Base provider schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    base_url: str | None = None
    api_key: str | None = None
    models: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)


class ProviderCreate(ProviderBase):
    """Provider creation schema."""


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
