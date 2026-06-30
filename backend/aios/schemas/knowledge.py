"""AIOS Knowledge Schemas."""

from typing import Any

from pydantic import BaseModel, Field


class KnowledgeIndex(BaseModel):
    """Knowledge index request schema."""
    source: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearch(BaseModel):
    """Knowledge search schema."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    source: str | None = None


class KnowledgeResponse(BaseModel):
    """Knowledge response schema."""
    id: str
    source: str
    content: str
    metadata: dict[str, Any]
    embedding: list[float] | None = None
    indexed_at: str

    class Config:
        from_attributes = True
