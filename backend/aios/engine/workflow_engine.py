"""AIOS Workflow Engine - DAG-based workflow execution.

This module provides the workflow engine that executes directed acyclic
graphs (DAGs) of tasks using the agent system.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

from aios.agents.base import AgentContext, AgentResult
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Workflow:
    """Represents a workflow as a directed acyclic graph of tasks."""

    def __init__(
        self,
        name: str,
        description: str = "",
        tasks: list[dict[str, Any]] | None = None,
        dependencies: dict[str, list[str]] | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.tasks = tasks or []
        self.dependencies = dependencies or {}
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.results: dict[str, AgentResult] = {}
        self.errors: list[str] = []

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": self.tasks,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "errors": self.errors,
        }


class WorkflowEngine:
    """Engine for executing workflow DAGs.

    Manages workflow lifecycle, task scheduling, and result collection.
    """

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}
        self._registry = AgentRegistry()
        self._logger = structlog.get_logger("aios.engine.workflow")

    def create_workflow(
        self,
        name: str,
        description: str = "",
        tasks: list[dict[str, Any]] | None = None,
        dependencies: dict[str, list[str]] | None = None,
    ) -> Workflow:
        """Create a new workflow.

        Args:
            name: Workflow name.
            description: Workflow description.
            tasks: List of task definitions.
            dependencies: Task dependency map.

        Returns:
            Created Workflow instance.
        """
        workflow = Workflow(
            name=name,
            description=description,
            tasks=tasks,
            dependencies=dependencies,
        )
        self._workflows[workflow.id] = workflow
        self._logger.info("Workflow created", workflow_id=workflow.id, name=name)
        return workflow

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get a workflow by ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            Workflow instance or None.
        """
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> list[dict[str, Any]]:
        """List all workflows.

        Returns:
            List of workflow dictionaries.
        """
        return [w.to_dict() for w in self._workflows.values()]

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: dict[str, Any] | None = None,
    ) -> Workflow:
        """Execute a workflow.

        Args:
            workflow_id: The workflow to execute.
            input_data: Input data for the workflow.

        Returns:
            The executed workflow with results.

        Raises:
            ValueError: If workflow not found.
        """
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()

        self._logger.info(
            "Workflow execution started",
            workflow_id=workflow_id,
            tasks_count=len(workflow.tasks),
        )

        try:
            executed = set()
            for task_def in workflow.tasks:
                task_id = task_def.get("id")
                if task_id and self._can_execute(task_id, workflow.dependencies, executed):
                    result = await self._execute_task(task_def, input_data or {})
                    workflow.results[task_id] = result
                    executed.add(task_id)

                    if not result.success:
                        workflow.errors.append(
                            f"Task {task_id} failed: {result.error}"
                        )

            if workflow.errors:
                workflow.status = WorkflowStatus.FAILED
            else:
                workflow.status = WorkflowStatus.COMPLETED

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append(str(e))
            self._logger.exception("Workflow execution failed", error=str(e))

        workflow.completed_at = datetime.utcnow()

        self._logger.info(
            "Workflow execution completed",
            workflow_id=workflow_id,
            status=workflow.status.value,
        )

        return workflow

    def _can_execute(
        self,
        task_id: str,
        dependencies: dict[str, list[str]],
        executed: set,
    ) -> bool:
        """Check if a task can be executed (all dependencies met).

        Args:
            task_id: The task to check.
            dependencies: The dependency map.
            executed: Set of already executed task IDs.

        Returns:
            True if the task can be executed.
        """
        deps = dependencies.get(task_id, [])
        return all(dep in executed for dep in deps)

    async def _execute_task(
        self,
        task_def: dict[str, Any],
        input_data: dict[str, Any],
    ) -> AgentResult:
        """Execute a single task.

        Args:
            task_def: Task definition.
            input_data: Input data for the task.

        Returns:
            AgentResult from execution.
        """
        task_id = task_def.get("id", str(uuid.uuid4()))
        agent_role = task_def.get("agent_role", "planner")

        agent = self._registry.create_agent(role=agent_role)

        context = AgentContext(
            task_id=task_id,
            task_type=task_def.get("type", "generic"),
            input_data={**input_data, **task_def.get("input", {})},
        )

        result = await agent.run(context)

        self._registry.remove_agent(agent.agent_id)

        return result

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow.

        Args:
            workflow_id: The workflow to cancel.

        Returns:
            True if cancelled.
        """
        workflow = self._workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.utcnow()
            self._logger.info("Workflow cancelled", workflow_id=workflow_id)
            return True
        return False
