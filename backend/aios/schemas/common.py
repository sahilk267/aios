"""AIOS Common Schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model."""
    id: str
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
