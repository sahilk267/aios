import asyncio

import pytest

from aios.agents.base import AgentContext, AgentStatus
from aios.agents.registry import AgentRegistry
from aios.engine.workflow_engine import WorkflowEngine, WorkflowStatus

"""End-to-end tests for agent lifecycle.

Tests the complete workflow from planning through QA,
including database and vector store updates.
"""


@pytest.mark.e2e
class TestAgentLifecycle:
    """E2E tests for the complete agent lifecycle."""

    @pytest.mark.asyncio
    async def test_planner_agent_lifecycle(self):
        """Test planner agent full lifecycle."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="planner", name="e2e-planner")

        assert agent.status == AgentStatus.IDLE

        context = AgentContext(
            task_id="e2e-plan-1",
            task_type="plan",
            input_data={"query": "Create a plan for user authentication"},
        )

        result = await agent.run(context)

        assert result.success is True
        assert result.output is not None
        assert "tasks" in result.output
        assert agent.status == AgentStatus.COMPLETED
        assert agent.total_tasks == 1
        assert agent.successful_tasks == 1

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_architect_agent_lifecycle(self):
        """Test architect agent full lifecycle."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="architect", name="e2e-architect")

        context = AgentContext(
            task_id="e2e-arch-1",
            task_type="architecture",
            input_data={"query": "Design a REST API for user management"},
        )

        result = await agent.run(context)

        assert result.success is True
        assert "components" in result.output
        assert agent.status == AgentStatus.COMPLETED

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_backend_engineer_lifecycle(self):
        """Test backend engineer agent lifecycle."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="backend_engineer", name="e2e-backend")

        context = AgentContext(
            task_id="e2e-backend-1",
            task_type="implementation",
            input_data={"query": "Implement user authentication endpoint"},
        )

        result = await agent.run(context)

        assert result.success is True
        assert "files" in result.output
        assert agent.status == AgentStatus.COMPLETED

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_reviewer_agent_lifecycle(self):
        """Test reviewer agent lifecycle."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="reviewer", name="e2e-reviewer")

        context = AgentContext(
            task_id="e2e-review-1",
            task_type="review",
            input_data={
                "code": "def hello():\n    print('hello')\n",
            },
        )

        result = await agent.run(context)

        assert result.success is True
        assert "score" in result.output
        assert agent.status == AgentStatus.COMPLETED

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_qa_agent_lifecycle(self):
        """Test QA agent lifecycle."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="qa", name="e2e-qa")

        context = AgentContext(
            task_id="e2e-qa-1",
            task_type="testing",
            input_data={"query": "Create tests for user authentication"},
        )

        result = await agent.run(context)

        assert result.success is True
        assert "test_cases" in result.output
        assert agent.status == AgentStatus.COMPLETED

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_full_workflow_pipeline(self):
        """Test complete workflow from planning to QA."""

        engine = WorkflowEngine()

        workflow = engine.create_workflow(
            name="E2E Test Workflow",
            description="Full pipeline test",
            tasks=[
                {
                    "id": "plan",
                    "type": "plan",
                    "agent_role": "planner",
                    "input": {"query": "Plan a simple feature"},
                },
                {
                    "id": "architect",
                    "type": "architecture",
                    "agent_role": "architect",
                    "input": {"query": "Design the architecture"},
                },
                {
                    "id": "implement",
                    "type": "implementation",
                    "agent_role": "backend_engineer",
                    "input": {"query": "Implement the feature"},
                },
                {
                    "id": "review",
                    "type": "review",
                    "agent_role": "reviewer",
                    "input": {"code": "def feature(): pass"},
                },
                {
                    "id": "test",
                    "type": "testing",
                    "agent_role": "qa",
                    "input": {"query": "Test the feature"},
                },
            ],
            dependencies={
                "plan": [],
                "architect": ["plan"],
                "implement": ["architect"],
                "review": ["implement"],
                "test": ["implement"],
            },
        )

        result = await engine.execute_workflow(workflow.id)

        assert result.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)
        assert result.started_at is not None
        assert result.completed_at is not None

        for task_def in workflow.tasks:
            task_id = task_def.get("id")
            assert task_id in result.results

    @pytest.mark.asyncio
    async def test_workflow_with_failure(self):
        """Test workflow handles task failure gracefully."""

        engine = WorkflowEngine()

        workflow = engine.create_workflow(
            name="Failure Test Workflow",
            tasks=[
                {
                    "id": "plan",
                    "type": "plan",
                    "agent_role": "planner",
                    "input": {},
                },
            ],
            dependencies={"plan": []},
        )

        result = await engine.execute_workflow(workflow.id)

        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_agent_metrics_tracking(self):
        """Test that agent metrics are tracked correctly."""

        registry = AgentRegistry()
        agent = registry.create_agent(role="planner", name="metrics-test")

        for i in range(3):
            context = AgentContext(
                task_id=f"metrics-{i}",
                task_type="plan",
                input_data={"query": f"Plan task {i}"},
            )
            await agent.run(context)

        metrics = agent.get_metrics()
        assert metrics["total_tasks"] == 3
        assert metrics["successful_tasks"] == 3
        assert metrics["success_rate"] == 1.0

        registry.remove_agent(agent.agent_id)

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self):
        """Test multiple agents can run concurrently."""

        registry = AgentRegistry()

        agents = [
            registry.create_agent(role="planner", name=f"concurrent-{i}")
            for i in range(3)
        ]

        contexts = [
            AgentContext(
                task_id=f"concurrent-{i}",
                task_type="plan",
                input_data={"query": f"Concurrent plan {i}"},
            )
            for i in range(3)
        ]

        results = await asyncio.gather(
            *[agent.run(ctx) for agent, ctx in zip(agents, contexts, strict=False)]
        )

        assert all(r.success for r in results)

        for agent in agents:
            registry.remove_agent(agent.agent_id)
