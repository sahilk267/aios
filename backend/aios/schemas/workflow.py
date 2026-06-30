"""AIOS Workflow Schemas."""

from typing import Any

from pydantic import BaseModel, Field


class TaskDefinition(BaseModel):
    """Task definition schema."""
    id: str
    type: str
    agent_role: str
    input: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    tasks: list[TaskDefinition] = Field(default_factory=list)
    dependencies: dict[str, list[str]] = Field(default_factory=dict)


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema."""


class WorkflowUpdate(BaseModel):
    """Workflow update schema."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    tasks: list[TaskDefinition] | None = None
    dependencies: dict[str, list[str]] | None = None


class WorkflowResponse(WorkflowBase):
    """Workflow response schema."""
    id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class WorkflowExecute(BaseModel):
    """Workflow execution schema."""
    input: dict[str, Any] = Field(default_factory=dict)
