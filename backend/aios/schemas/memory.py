"""AIOS Memory Schemas."""

from typing import Any

from pydantic import BaseModel, Field


class MemoryStore(BaseModel):
    """Memory store schema."""
    type: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemorySearch(BaseModel):
    """Memory search schema."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    memory_type: str | None = None


class MemoryResponse(BaseModel):
    """Memory response schema."""
    id: str
    type: str
    content: str
    metadata: dict[str, Any]
    embedding: list[float] | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
