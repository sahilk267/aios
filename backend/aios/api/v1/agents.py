"""AIOS Agent Endpoints."""


import structlog
from fastapi import APIRouter, HTTPException, Query

from aios.schemas.agent import AgentCreate, AgentResponse, AgentUpdate, TaskRequest, TaskResponse

logger = structlog.get_logger(__name__)

router = APIRouter()

# In-memory store for now
_agents: dict = {}
_tasks: dict = {}


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: str | None = None,
) -> list[AgentResponse]:
    """List all agents."""
    agents = list(_agents.values())
    if role:
        agents = [a for a in agents if a.get("role") == role]
    return agents[skip : skip + limit]


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(agent: AgentCreate) -> AgentResponse:
    """Create a new agent."""
    import uuid
    from datetime import datetime

    agent_id = str(uuid.uuid4())
    agent_data = {
        "id": agent_id,
        "name": agent.name,
        "role": agent.role,
        "description": agent.description,
        "provider": agent.provider,
        "model": agent.model,
        "status": "idle",
        "config": agent.config or {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _agents[agent_id] = agent_data
    logger.info("Agent created", agent_id=agent_id, name=agent.name, role=agent.role)
    return AgentResponse(**agent_data)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get an agent by ID."""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**_agents[agent_id])


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, agent: AgentUpdate) -> AgentResponse:
    """Update an agent."""
    from datetime import datetime

    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    existing = _agents[agent_id]
    for field in ["name", "description", "provider", "model", "config"]:
        value = getattr(agent, field, None)
        if value is not None:
            existing[field] = value
    existing["updated_at"] = datetime.utcnow().isoformat()

    logger.info("Agent updated", agent_id=agent_id)
    return AgentResponse(**existing)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str) -> None:
    """Delete an agent."""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    del _agents[agent_id]
    logger.info("Agent deleted", agent_id=agent_id)


@router.post("/{agent_id}/execute", response_model=TaskResponse)
async def execute_agent_task(agent_id: str, task: TaskRequest) -> TaskResponse:
    """Execute a task on an agent."""
    import uuid
    from datetime import datetime

    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = _agents[agent_id]
    task_id = str(uuid.uuid4())

    task_data = {
        "id": task_id,
        "agent_id": agent_id,
        "type": task.type,
        "input": task.input,
        "status": "pending",
        "output": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    _tasks[task_id] = task_data

    # Update agent status
    agent["status"] = "running"
    agent["updated_at"] = datetime.utcnow().isoformat()

    logger.info("Task created", task_id=task_id, agent_id=agent_id, type=task.type)
    return TaskResponse(**task_data)


@router.get("/{agent_id}/tasks", response_model=list[TaskResponse])
async def list_agent_tasks(agent_id: str) -> list[TaskResponse]:
    """List tasks for an agent."""
    tasks = [t for t in _tasks.values() if t["agent_id"] == agent_id]
    return [TaskResponse(**t) for t in tasks]
