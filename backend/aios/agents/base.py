"""AIOS BaseAgent - Abstract agent with lifecycle management.

This module provides the foundation for all AIOS agents. It defines the agent
lifecycle, context management, and result handling.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle states."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentContext:
    """Context passed to agents during execution.

    Contains all information an agent needs to perform its task,
    including project state, memory, and conversation history.
    """

    def __init__(
        self,
        task_id: str,
        task_type: str,
        input_data: dict[str, Any],
        project_id: str | None = None,
        parent_agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.input_data = input_data
        self.project_id = project_id
        self.parent_agent_id = parent_agent_id
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.memory: list[dict[str, Any]] = []
        self.artifacts: dict[str, Any] = {}

    def add_memory(self, memory_type: str, content: str, **kwargs) -> None:
        """Add a memory entry to the context."""
        self.memory.append({
            "type": memory_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs,
        })

    def add_artifact(self, name: str, data: Any) -> None:
        """Add an artifact to the context."""
        self.artifacts[name] = {
            "data": data,
            "created_at": datetime.utcnow().isoformat(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "input_data": self.input_data,
            "project_id": self.project_id,
            "parent_agent_id": self.parent_agent_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "memory": self.memory,
            "artifacts": {k: v["data"] for k, v in self.artifacts.items()},
        }


class AgentResult:
    """Result of agent execution."""

    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: str | None = None,
        artifacts: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.success = success
        self.output = output
        self.error = error
        self.artifacts = artifacts or {}
        self.metrics = metrics or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "id": self.id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def success(cls, output: Any = None, **kwargs) -> "AgentResult":
        """Create a successful result."""
        return cls(success=True, output=output, **kwargs)

    @classmethod
    def failure(cls, error: str, **kwargs) -> "AgentResult":
        """Create a failed result."""
        return cls(success=False, error=error, **kwargs)


class BaseAgent(ABC):
    """Abstract base class for all AIOS agents.

    All agents must inherit from this class and implement the `execute` method.
    The class provides lifecycle management, logging, and error handling.

    Attributes:
        agent_id: Unique identifier for this agent instance.
        name: Human-readable name for the agent.
        role: The role this agent performs.
        provider: The AI provider to use for LLM calls.
        model: The specific model to use.
        config: Additional configuration options.
    """

    # Override in subclasses
    ROLE: str = "base"
    DESCRIPTION: str = "Base agent"
    CAPABILITIES: list[str] = []

    def __init__(
        self,
        name: str | None = None,
        provider: str = "ollama",
        model: str = "llama3",
        config: dict[str, Any] | None = None,
    ):
        self.agent_id = str(uuid.uuid4())
        self.name = name or f"{self.ROLE}-{self.agent_id[:8]}"
        self.role = self.ROLE
        self.provider = provider
        self.model = model
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.created_at = datetime.utcnow()
        self.last_active = None
        self.total_tasks = 0
        self.successful_tasks = 0
        self._logger = structlog.get_logger(
            "aios.agent",
            agent_id=self.agent_id,
            agent_name=self.name,
            agent_role=self.role,
        )

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task.

        Args:
            context: The execution context containing task details.

        Returns:
            AgentResult containing the outcome of execution.
        """
        ...

    async def initialize(self) -> None:
        """Initialize the agent before execution.

        Override this method to perform setup tasks.
        """
        self.status = AgentStatus.INITIALIZING
        self._logger.info("Agent initialized")

    async def cleanup(self) -> None:
        """Clean up after execution.

        Override this method to perform cleanup tasks.
        """
        self._logger.info("Agent cleaned up")

    async def run(self, context: AgentContext) -> AgentResult:
        """Run the agent with full lifecycle management.

        This method handles initialization, execution, cleanup,
        and error handling.

        Args:
            context: The execution context.

        Returns:
            AgentResult containing the outcome.
        """
        self._logger.info("Agent starting", task_id=context.task_id)
        self.status = AgentStatus.RUNNING
        self.last_active = datetime.utcnow()
        self.total_tasks += 1

        try:
            # Initialize
            await self.initialize()

            # Execute
            result = await self.execute(context)

            # Update metrics
            if result.success:
                self.successful_tasks += 1
                self.status = AgentStatus.COMPLETED
            else:
                self.status = AgentStatus.FAILED

            self._logger.info(
                "Agent completed",
                task_id=context.task_id,
                success=result.success,
            )

            return result

        except Exception as e:
            self.status = AgentStatus.FA._logger.error(
                "Agent execution failed",
                task_id=context.task_id,
                error=str(e),
            )
            return AgentResult.failure(
                error=str(e),
                metrics=self.get_metrics(),
            )
        finally:
            await self.cleanup()

    async def cancel(self) -> None:
        """Cancel the agent's current execution."""
        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.CANCELLED
            self._logger.info("Agent cancelled")

    def get_metrics(self) -> dict[str, Any]:
        """Get agent performance metrics."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "total_tasks": self.total_tasks,
            "successful_tasks": self.successful_tasks,
            "success_rate": (
                self.successful_tasks / self.total_tasks
                if self.total_tasks > 0
                else 0.0
            ),
            "created_at": self.created_at.isoformat(),
            "last_active": (
                self.last_active.isoformat() if self.last_active else None
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert agent state to dictionary."""
        return {
            "id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "provider": self.provider,
            "model": self.model,
            "status": self.status.value,
            "config": self.config,
            "capabilities": self.CAPABILITIES,
            "metrics": self.get_metrics(),
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"id={self.agent_id[:8]} "
            f"name={self.name} "
            f"status={self.status.value}>"
        )
