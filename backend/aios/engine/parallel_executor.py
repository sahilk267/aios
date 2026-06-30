"""AIOS Parallel Executor - Concurrent task execution."""

import asyncio
from collections.abc import Callable
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ParallelExecutor:
    """Executes multiple tasks concurrently with semaphore-based limiting."""

    def __init__(self, max_concurrent: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._logger = structlog.get_logger("aios.engine.parallel")

    async def execute(
        self,
        tasks: list[Callable],
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        """Execute tasks concurrently.

        Args:
            tasks: List of async callables.
            *args: Positional arguments for each task.
            **kwargs: Keyword arguments for each task.

        Returns:
            List of results.
        """
        async def _run(task: Callable) -> Any:
            async with self._semaphore:
                return await task(*args, **kwargs)

        return await asyncio.gather(*[_run(t) for t in tasks], return_exceptions=True)

    async def execute_with_results(
        self,
        tasks: dict[str, Callable],
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute named tasks concurrently.

        Args:
            tasks: Dictionary of task name to async callable.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            Dictionary of task name to result.
        """
        async def _run(name: str, task: Callable) -> tuple:
            async with self._semaphore:
                try:
                    result = await task(*args, **kwargs)
                    return name, {"success": True, "result": result}
                except Exception as e:
                    return name, {"success": False, "error": str(e)}

        results = await asyncio.gather(
            *[_run(name, task) for name, task in tasks.items()]
        )
        return dict(results)


# Global instance
parallel_executor = ParallelExecutor()
