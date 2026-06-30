"""AIOS Project Endpoints."""


import structlog
from fastapi import APIRouter, HTTPException, Query

from aios.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now (will be replaced with database)
_projects: dict = {}


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> list[ProjectResponse]:
    """List all projects."""
    projects = list(_projects.values())
    return projects[skip : skip + limit]


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(project: ProjectCreate) -> ProjectResponse:
    """Create a new project."""
    import uuid
    from datetime import datetime

    project_id = str(uuid.uuid4())
    project_data = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "path": project.path,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _projects[project_id] = project_data
    logger.info("Project created", project_id=project_id, name=project.name)
    return ProjectResponse(**project_data)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    """Get a project by ID."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**_projects[project_id])


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project: ProjectUpdate) -> ProjectResponse:
    """Update a project."""
    from datetime import datetime

    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = _projects[project_id]
    if project.name is not None:
        existing["name"] = project.name
    if project.description is not None:
        existing["description"] = project.description
    if project.status is not None:
        existing["status"] = project.status
    existing["updated_at"] = datetime.utcnow().isoformat()

    logger.info("Project updated", project_id=project_id)
    return ProjectResponse(**existing)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str) -> None:
    """Delete a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found")
    del _projects[project_id]
    logger.info("Project deleted", project_id=project_id)
