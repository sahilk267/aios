"""AIOS Project Schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    path: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
