"""AIOS Memory Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryStore(BaseModel):
    """Memory store schema."""
    type: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemorySearch(BaseModel):
    """Memory search schema."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    memory_type: Optional[str] = None


class MemoryResponse(BaseModel):
    """Memory response schema."""
    id: str
    type: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
