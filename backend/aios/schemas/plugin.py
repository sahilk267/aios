"""AIOS Plugin Schemas."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PluginBase(BaseModel):
    """Base plugin schema."""
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., min_length=1, max_length=50)
    version: str = Field("0.1.0", pattern=r"^\d+\.\d+\.\d+$")
    config: Dict[str, Any] = Field(default_factory=dict)


class PluginCreate(PluginBase):
    """Plugin creation schema."""
    pass


class PluginResponse(PluginBase):
    """Plugin response schema."""
    id: str
    status: str
    installed_at: str

    class Config:
        from_attributes = True
