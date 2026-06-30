"""AIOS Project Schemas."""


from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    path: str | None = None


class ProjectCreate(ProjectBase):
    """Project creation schema."""


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: str
    status: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
