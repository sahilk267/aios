"""AIOS Knowledge Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class KnowledgeIndex(BaseModel):
    """Knowledge index request schema."""
    source: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearch(BaseModel):
    """Knowledge search schema."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    source: Optional[str] = None


class KnowledgeResponse(BaseModel):
    """Knowledge response schema."""
    id: str
    source: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    indexed_at: str

    class Config:
        from_attributes = True
