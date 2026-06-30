"""AIOS Dependency Resolver - DAG dependency resolution."""

from collections import deque

import structlog

logger = structlog.get_logger(__name__)


class DependencyResolver:
    """Resolves task dependencies using topological sorting."""

    def __init__(self):
        self._logger = structlog.get_logger("aios.engine.dependency")

    def resolve(
        self,
        tasks: list[str],
        dependencies: dict[str, list[str]],
    ) -> list[str]:
        """Resolve execution order using topological sort.

        Args:
            tasks: List of task identifiers.
            dependencies: Map of task to its dependencies.

        Returns:
            Ordered list of tasks.

        Raises:
            ValueError: If circular dependency detected.
        """
        in_degree: dict[str, int] = dict.fromkeys(tasks, 0)
        graph: dict[str, list[str]] = {task: [] for task in tasks}

        for task, deps in dependencies.items():
            if task not in in_degree:
                continue
            for dep in deps:
                if dep in graph:
                    graph[dep].append(task)
                    in_degree[task] += 1

        queue = deque([t for t in tasks if in_degree[t] == 0])
        result = []

        while queue:
            task = queue.popleft()
            result.append(task)
            for dependent in graph[task]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(tasks):
            raise ValueError("Circular dependency detected")

        return result

    def get_ready_tasks(
        self,
        tasks: list[str],
        dependencies: dict[str, list[str]],
        completed: set[str],
    ) -> list[str]:
        """Get tasks that are ready to execute.

        Args:
            tasks: All task identifiers.
            dependencies: Dependency map.
            completed: Set of completed task IDs.

        Returns:
            List of tasks whose dependencies are all met.
        """
        ready = []
        for task in tasks:
            if task in completed:
                continue
            deps = dependencies.get(task, [])
            if all(dep in completed for dep in deps):
                ready.append(task)
        return ready

    def validate(
        self,
        tasks: list[str],
        dependencies: dict[str, list[str]],
    ) -> bool:
        """Validate that dependencies are consistent.

        Args:
            tasks: All task identifiers.
            dependencies: Dependency map.

        Returns:
            True if valid.
        """
        try:
            self.resolve(tasks, dependencies)
            return True
        except ValueError:
            return False


# Global instance
dependency_resolver = DependencyResolver()
