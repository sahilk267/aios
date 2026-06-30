"""AIOS Planner Agent - Task planning and decomposition."""

from typing import Any

import structlog

from aios.agents.base import AgentContext, AgentResult, BaseAgent
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)


@AgentRegistry.register
@AgentRegistry.register
class PlannerAgent(BaseAgent):
    """Agent responsible for planning and decomposing tasks.

    The Planner agent analyzes requirements and breaks them down into
    actionable subtasks that can be executed by other agents.
    """

    ROLE = "planner"
    DESCRIPTION = "Analyzes requirements and creates implementation plans"
    CAPABILITIES = [
        "task_decomposition",
        "requirement_analysis",
        "dependency_identification",
        "effort_estimation",
    ]

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute planning task.

        Analyzes the input requirements and produces a structured plan
        with subtasks, dependencies, and effort estimates.
        """
        self._logger.info("Planner starting", task_id=context.task_id)

        try:
            query = context.input_data.get("query", "")
            if not query:
                return AgentResult.failure("No query provided for planning")

            # Create plan structure
            plan = self._create_plan(query, context)

            # Add plan to context artifacts
            context.add_artifact("plan", plan)
            context.add_memory("plan", f"Created plan with {len(plan['tasks'])} tasks")

            self._logger.info(
                "Planner completed",
                task_id=context.task_id,
                tasks_count=len(plan["tasks"]),
            )

            return AgentResult.success(
                output=plan,
                artifacts={"plan": plan},
                metrics={"tasks_planned": len(plan["tasks"])},
            )

        except Exception as e:
            self._logger.exception("Planner failed", error=str(e))
            return AgentResult.failure(f"Planning failed: {e!s}")

    def _create_plan(self, query: str, context: AgentContext) -> dict[str, Any]:
        """Create a structured plan from the query."""
        return {
            "query": query,
            "tasks": [
                {
                    "id": "analyze",
                    "type": "analysis",
                    "description": f"Analyze requirements for: {query}",
                    "agent_role": "architect",
                    "priority": "high",
                    "estimated_effort": "medium",
                    "depends_on": [],
                },
                {
                    "id": "implement",
                    "type": "implementation",
                    "description": "Implement the solution",
                    "agent_role": "backend_engineer",
                    "priority": "high",
                    "estimated_effort": "high",
                    "depends_on": ["analyze"],
                },
                {
                    "id": "review",
                    "type": "review",
                    "description": "Review the implementation",
                    "agent_role": "reviewer",
                    "priority": "medium",
                    "estimated_effort": "low",
                    "depends_on": ["implement"],
                },
                {
                    "id": "test",
                    "type": "testing",
                    "description": "Test the implementation",
                    "agent_role": "qa",
                    "priority": "medium",
                    "estimated_effort": "medium",
                    "depends_on": ["implement"],
                },
            ],
            "dependencies": {
                "analyze": [],
                "implement": ["analyze"],
                "review": ["implement"],
                "test": ["implement"],
            },
            "metadata": {
                "created_by": self.name,
                "total_tasks": 4,
                "estimated_total_effort": "high",
            },
        }
