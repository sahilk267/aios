"""AIOS Agent Schemas."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    provider: Optional[str] = "ollama"
    model: Optional[str] = "llama3"
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentCreate(AgentBase):
    """Agent creation schema."""
    pass


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    """Agent response schema."""
    id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TaskRequest(BaseModel):
    """Task request schema."""
    type: str = Field(..., min_length=1, max_length=100)
    input: Dict[str, Any] = Field(default_factory=dict)
    priority: Optional[int] = Field(0, ge=0, le=10)


class TaskResponse(BaseModel):
    """Task response schema."""
    id: str
    agent_id: str
    type: str
    input: Dict[str, Any]
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
