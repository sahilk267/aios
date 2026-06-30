"""AIOS Task Scheduler - Async task scheduling and execution.

This module provides task scheduling capabilities for the workflow engine.
"""

import uuid
from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents a schedulable task."""

    def __init__(
        self,
        name: str,
        func: Callable,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        priority: int = 0,
        timeout: int | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.priority = priority
        self.timeout = timeout
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: str | None = None
        self.created_at = datetime.utcnow()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class TaskScheduler:
    """Schedules and executes async tasks.

    Manages task queue, concurrency, and execution lifecycle.
    """

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self._queue: list[Task] = []
        self._running: dict[str, Task] = {}
        self._completed: dict[str, Task] = {}
        self._logger = structlog.get_logger("aios.engine.scheduler")

    def schedule(
        self,
        name: str,
        func: Callable,
        args: tuple | None = None,
        kwargs: dict[str, Any] | None = None,
        priority: int = 0,
    ) -> Task:
        """Schedule a task for execution.

        Args:
            name: Task name.
            func: Async function to execute.
            args: Positional arguments.
            kwargs: Keyword arguments.
            priority: Task priority (higher = more important).

        Returns:
            Scheduled Task instance.
        """
        task = Task(
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
        )
        self._queue.append(task)
        self._queue.sort(key=lambda t: t.priority, reverse=True)

        self._logger.info("Task scheduled", task_id=task.id, name=name)
        return task

    async def run(self, task: Task) -> Task:
        """Run a task immediately.

        Args:
            task: The task to run.

        Returns:
            The task with results.
        """
        if len(self._running) >= self.max_concurrent:
            task.status = TaskStatus.QUEUED
            self._logger.info("Task queued", task_id=task.id)
            return task

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        self._running[task.id] = task

        try:
            import asyncio
            result = await asyncio.wait_for(
                task.func(*task.args, **task.kwargs),
                timeout=task.timeout,
            )
            task.result = result
            task.status = TaskStatus.COMPLETED
        except TimeoutError:
            task.error = "Task timed out"
            task.status = TaskStatus.FAILED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
        finally:
            task.completed_at = datetime.utcnow()
            del self._running[task.id]
            self._completed[task.id] = task

        return task

    async def run_all(self) -> list[Task]:
        """Run all queued tasks.

        Returns:
            List of completed tasks.
        """
        import asyncio

        tasks = []
        while self._queue:
            task = self._queue.pop(0)
            tasks.append(self.run(task))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return [self._completed.get(t.id, t) for t in tasks]

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID.

        Args:
            task_id: The task ID.

        Returns:
            Task instance or None.
        """
        if task_id in self._running:
            return self._running[task_id]
        if task_id in self._completed:
            return self._completed[task_id]
        for task in self._queue:
            if task.id == task_id:
                return task
        return None

    def get_stats(self) -> dict[str, int]:
        """Get scheduler statistics.

        Returns:
            Dictionary with task counts.
        """
        return {
            "queued": len(self._queue),
            "running": len(self._running),
            "completed": len(self._completed),
        }
