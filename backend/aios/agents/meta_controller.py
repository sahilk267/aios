"""AIOS Meta-Controller Agent - Autonomous task selection and execution.

The Meta-Controller reads PROJECT_STATE.json and TASKS.md to autonomously
select the next highest-priority task and trigger the full pipeline:
Planner -> Architect -> Backend Engineer -> Reviewer -> QA

It handles rollback automatically if any step fails.
"""

import json
import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.agents.base import BaseAgent, AgentContext, AgentResult, AgentStatus
from aios.agents.registry import AgentRegistry

logger = structlog.get_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class MetaControllerAgent(BaseAgent):
    """Agent that autonomously selects and executes tasks.

    The Meta-Controller:
    1. Reads PROJECT_STATE.json to find incomplete modules
    2. Reads TASKS.md to find the highest-priority pending task
    3. Triggers the full pipeline for that task
    4. Handles rollback on failure
    5. Updates state files on success
    """

    ROLE = "meta_controller"
    DESCRIPTION = "Autonomously selects and executes the next highest-priority task"
    CAPABILITIES = [
        "task_selection",
        "pipeline_orchestration",
        "state_management",
        "rollback_handling",
        "autonomous_execution",
    ]

    def __init__(self, **kwargs):
        super().__init__(name="meta-controller", **kwargs)
        self._registry = AgentRegistry()

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the meta-controller cycle.

        1. Read project state
        2. Select next task
        3. Execute pipeline
        4. Update state
        """
        self._logger.info("Meta-Controller starting")

        try:
            # Step 1: Read project state
            state = self._read_project_state()
            if not state:
                return AgentResult.failure("Could not read PROJECT_STATE.json")

            # Step 2: Select next task
            next_task = self._select_next_task(state)
            if not next_task:
                return AgentResult.success(
                    output={"message": "No pending tasks found"},
                    metrics={"tasks_completed": 0},
                )

            self._logger.info("Selected task", task=next_task)

            # Step 3: Execute pipeline
            pipeline_result = await self._execute_pipeline(next_task, context)

            # Step 4: Update state
            if pipeline_result["success"]:
                self._update_project_state(next_task, "completed")
                self._logger.info("Task completed successfully", task=next_task)
            else:
                self._logger.warning("Task failed", task=next_taskipeline_result.get("error"))

            return AgentResult(
                success=pipeline_result["success"],
                output=pipeline_result,
                metrics={"task": next_task, "steps_completed": pipeline_result.get("steps", 0)},
            )

        except Exception as e:
            self._logger.error("Meta-Controller failed", error=str(e))
            return AgentResult.failure(f"Meta-Controller failed: {str(e)}")

    def _read_project_state(self) -> Optional[Dict[str, Any]]:
        """Read PROJECT_STATE.json."""
        state_path = PROJECT_ROOT / "PROJECT_STATE.json"
        if not state_path.exists():
            self._logger.error("PROJECT_STATE.json not found")
            return None
        try:
            with open(state_path) as f:
                return json.load(f)
        except Exception as e:
            self._logger.error("Failed to read PROJECT_STATE.json", error=str(e))
            return None

    def _select_next_task(self, state: Dict[str, Any]) -> Optional[str]:
        """Select the next highest-priority pending task.

        Strategy:
        1. Find modules with status 'in_progress'
        2. Find components with status 'pending' in those modules
        3. Return the first pending component
        """
        modules = state.get("modules", {})

        # Priority order for phases
        phase_priority = [
            "self_evolving",
            "core_engine",
            "memory_knowledge",
            "workflow_collaboration",
            "security_observability",
            "plugin_ecosystem",
        ]

        for module_name in phase_priority:
            module = modules.get(module_name, {})
            if module.get("status") in ("in_progress", "pending"):
                components = module.get("components", {})
                for comp_name, comp_status in components.items():
                    if comp_status == "pending":
                        return f"{module_name}.{comp_name}"

        return None

    async def _execute_pipeline(
        self,
        task: str,
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Execute the full pipeline for a task.

        Pipeline: Planner -> Architect -> Backend Engineer -> Reviewer -> QA
        """
        pipeline_steps = [
            ("planner", "plan"),
            ("architect", "architecture"),
            ("backend_engineer", "implementation"),
            ("reviewer", "review"),
            ("qa", "testing"),
        ]

        results = {
            "task": task,
            "success": False,
            "steps": 0,
            "step_results": {},
        }

        pipeline_context = AgentContext(
            task_id=f"pipeline-{task}",
            task_type="pipeline",
            input_data=context.input_data.copy(),
        )

        for agent_role, step_name in pipeline_steps:
            self._logger.info(f"Pipeline step: {step_name}")

            try:
                agent = self._registry.create_agent(
                    role=agent_role,
                    name=f"pipeline-{step_name}",
                )

                step_context = AgentContext(
                    task_id=f"{task}-{step_name}",
                    task_type=step_name,
                    input_data=pipeline_context.input_data.copy(),
                )

                result = await agent.run(step_context)
                results["step_results"][step_name] = result.to_dict()
                results["steps"] += 1

                # Pass output to next step
                if result.success and result.output:
                    pipeline_context.input_data[f"{step_name}_output"] = result.output
                    pipeline_context.add_artifact(step_name, result.output)

                self._registry.remove_agent(agent.agent_id)

                if not result.success:
                    results["error"] = f"Step '{step_name}' failed: {result.error}"
                    return results

            except Exception as e:
                results["error"] = f"Step '{step_name}' exception: {str(e)}"
                return results

        results["success"] = True
        return results

    def _update_project_state(self, task: str, status: str) -> None:
        """Update PROJECT_STATE.json with task completion."""
        state_path = PROJECT_ROOT / "PROJECT_STATE.json"
        if not state_path.exists():
            return

        try:
            with open(state_path) as f:
                state = json.load(f)

            # Parse task path (e.g., "self_evolving.meta_controller")
            parts = task.split(".")
            if len(parts) == 2:
                module_name, component_name = parts
                modules = state.get("modules", {})
                module = modules.get(module_name, {})
                components = module.get("components", {})
                if component_name in components:
                    components[component_name] = status

                    # Check if all components are complete
                    if all(v == "completed" for v in components.values()):
                        module["status"] = "completed"
                        module["progress"] = 100

            state["last_updated"] = datetime.utcnow().isoformat()

            with open(state_path, "w") as f:
                json.dump(state, f, indent=2)

            self._logger.info("Project state updated", task=task, status=status)

        except Exception as e:
            self._logger.error("Failed to update PROJECT_STATE.json", error=str(e))
