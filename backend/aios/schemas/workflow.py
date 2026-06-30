"""AIOS Workflow Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskDefinition(BaseModel):
    """Task definition schema."""
    id: str
    type: str
    agent_role: str
    input: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[str] = Field(default_factory=list)


class WorkflowBase(BaseModel):
    """Base workflow schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    tasks: List[TaskDefinition] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)


class WorkflowCreate(WorkflowBase):
    """Workflow creation schema."""
    pass


class WorkflowUpdate(BaseModel):
    """Workflow update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tasks: Optional[List[TaskDefinition]] = None
    dependencies: Optional[Dict[str, List[str]]] = None


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
    input: Dict[str, Any] = Field(default_factory=dict)
