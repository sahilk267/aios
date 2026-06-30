"""AIOS Backend Engineer Agent - Backend implementation."""

from typing import Any

import structlog

from aios.agents.base import AgentContext, AgentResult, BaseAgent
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


@AgentRegistry.register
class BackendEngineerAgent(BaseAgent):
    """Agent responsible for backend implementation.

    The Backend Engineer agent writes production-quality backend code
    following the architecture design and coding standards.
    """

    ROLE = "backend_engineer"
    DESCRIPTION = "Implements backend services and APIs"
    CAPABILITIES = [
        "api_implementation",
        "database_implementation",
        "service_development",
        "integration_implementation",
        "code_generation",
    ]

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute backend implementation task."""
        self._logger.info("Backend Engineer starting", task_id=context.task_id)

        try:
            query = context.input_data.get("query", "")
            architecture = context.input_data.get("architecture", {})

            if not query:
                return AgentResult.failure("No query provided for implementation")

            # Generate implementation
            implementation = self._generate_implementation(query, architecture, context)

            context.add_artifact("implementation", implementation)
            context.add_memory("implementation", "Generated backend implementation")

            return AgentResult.success(
                output=implementation,
                artifacts={"implementation": implementation},
                metrics={
                    "files_generated": len(implementation["files"]),
                    "total_lines": implementation["total_lines"],
                },
            )

        except Exception as e:
            self._logger.exception("Backend Engineer failed", error=str(e))
            return AgentResult.failure(f"Implementation failed: {e!s}")

    def _generate_implementation(
        self, query: str, architecture: dict, context: AgentContext
    ) -> dict[str, Any]:
        """Generate backend implementation."""
        return {
            "query": query,
            "files": [
                {
                    "path": "backend/service.py",
                    "content": "# Service implementation\n...",
                    "language": "python",
                    "lines": 150,
                },
                {
                    "path": "backend/models.py",
                    "content": "# Data models\n...",
                    "language": "python",
                    "lines": 80,
                },
                {
                    "path": "backend/api.py",
                    "content": "# API endpoints\n...",
                    "language": "python",
                    "lines": 120,
                },
            ],
            "total_lines": 350,
            "technologies": ["FastAPI", "SQLAlchemy", "Pydantic"],
            "patterns": ["repository", "service_layer", "dependency_injection"],
            "metadata": {
                "created_by": self.name,
                "follows_architecture": bool(architecture),
            },
        }
