"""AIOS Workflow Endpoints."""


import structlog
from fastapi import APIRouter, HTTPException, Query

from aios.schemas.workflow import WorkflowCreate, WorkflowExecute, WorkflowResponse, WorkflowUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now
_workflows: dict = {}
_workflow_runs: dict = {}


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = None,
) -> list[WorkflowResponse]:
    """List all workflows."""
    workflows = list(_workflows.values())
    if status:
        workflows = [w for w in workflows if w.get("status") == status]
    return workflows[skip : skip + limit]


@router.post("", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow: WorkflowCreate) -> WorkflowResponse:
    """Create a new workflow."""
    import uuid
    from datetime import datetime

    workflow_id = str(uuid.uuid4())
    workflow_data = {
        "id": workflow_id,
        "name": workflow.name,
        "description": workflow.description,
        "tasks": [t.model_dump() for t in workflow.tasks],
        "dependencies": workflow.dependencies or {},
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _workflows[workflow_id] = workflow_data
    logger.info("Workflow created", workflow_id=workflow_id, name=workflow.name)
    return WorkflowResponse(**workflow_data)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """Get a workflow by ID."""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse(**_workflows[workflow_id])


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(workflow_id: str, workflow: WorkflowUpdate) -> WorkflowResponse:
    """Update a workflow."""
    from datetime import datetime

    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    existing = _workflows[workflow_id]
    for field in ["name", "description", "tasks", "dependencies"]:
        value = getattr(workflow, field, None)
        if value is not None:
            if field == "tasks":
                existing[field] = [t.model_dump() for t in value]
            else:
                existing[field] = value
    existing["updated_at"] = datetime.utcnow().isoformat()

    logger.info("Workflow updated", workflow_id=workflow_id)
    return WorkflowResponse(**existing)


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str) -> None:
    """Delete a workflow."""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    del _workflows[workflow_id]
    logger.info("Workflow deleted", workflow_id=workflow_id)


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, execute: WorkflowExecute) -> dict:
    """Execute a workflow."""
    import uuid
    from datetime import datetime

    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    run_id = str(uuid.uuid4())
    run_data = {
        "id": run_id,
        "workflow_id": workflow_id,
        "status": "running",
        "input": execute.input or {},
        "output": None,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }
    _workflow_runs[run_id] = run_data

    # Update workflow status
    _workflows[workflow_id]["status"] = "running"
    _workflows[workflow_id]["updated_at"] = datetime.utcnow().isoformat()

    logger.info("Workflow execution started", run_id=run_id, workflow_id=workflow_id)
    return run_data


@router.get("/{workflow_id}/runs")
async def list_workflow_runs(workflow_id: str) -> list[dict]:
    """List workflow runs."""
    return [r for r in _workflow_runs.values() if r["workflow_id"] == workflow_id]
