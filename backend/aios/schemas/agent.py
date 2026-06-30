"""AIOS Agent Schemas."""

from typing import Any

from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base agent schema."""
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    provider: str | None = "ollama"
    model: str | None = "llama3"
    config: dict[str, Any] | None = Field(default_factory=dict)


class AgentCreate(AgentBase):
    """Agent creation schema."""


class AgentUpdate(BaseModel):
    """Agent update schema."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    provider: str | None = None
    model: str | None = None
    config: dict[str, Any] | None = None


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
    input: dict[str, Any] = Field(default_factory=dict)
    priority: int | None = Field(0, ge=0, le=10)


class TaskResponse(BaseModel):
    """Task response schema."""
    id: str
    agent_id: str
    type: str
    input: dict[str, Any]
    status: str
    output: Any | None = None
    error: str | None = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
