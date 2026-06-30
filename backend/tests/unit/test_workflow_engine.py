"""Tests for workflow engine."""

import pytest
from aios.engine.workflow_engine import (
    WorkflowEngine,
    Workflow,
    WorkflowStatus,
)


class TestWorkflow:
    """Test Workflow class."""

    def test_create_workflow(self):
        """Test workflow creation."""
        workflow = Workflow(
            name="Test Workflow",
            description="A test workflow",
        )
        assert workflow.name == "Test Workflow"
        assert workflow.status == WorkflowStatus.PENDING
        assert workflow.tasks == []

    def test_workflow_to_dict(self):
        """Test workflow serialization."""
        workflow = Workflow(name="Test")
        d = workflow.to_dict()
        assert d["name"] == "Test"
        assert d["status"] == "pending"
        assert "id" in d


class TestWorkflowEngine:
    """Test WorkflowEngine class."""

    def test_create_workflow(self):
        """Test creating workflow via engine."""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(
            name="Test Flow",
            description="Testing",
            tasks=[
                {"id": "task1", "type": "plan", "agent_role": "planner"},
            ],
        )
        assert workflow.name == "Test Flow"
        assert len(workflow.tasks) == 1

    def test_get_workflow(self):
        """Test getting workflow by ID."""
        engine = WorkflowEngine()
        created = engine.create_workflow(name="Test")
        fetched = engine.get_workflow(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_nonexistent_workflow(self):
        """Test getting nonexistent workflow."""
        engine = WorkflowEngine()
        assert engine.get_workflow("nonexistent") is None

    def test_list_workflows(self):
        """Test listing workflows."""
        engine = WorkflowEngine()
        engine.create_workflow(name="Flow 1")
        engine.create_workflow(name="Flow 2")
        workflows = engine.list_workflows()
        assert len(workflows) == 2

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test executing a workflow."""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(
            name="Test Flow",
            tasks=[
                {
                    "id": "plan-task",
                    "type": "plan",
                    "agent_role": "planner",
                    "input": {"query": "test plan"},
                },
            ],
        )

        result = await engine.execute_workflow(workflow.id)
        assert result.status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED)
        assert result.started_at is not None
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_execute_nonexistent_workflow(self):
        """Test executing nonexistent workflow raises error."""
        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="Workflow not found"):
            await engine.execute_workflow("nonexistent")

    @pytest.mark.asyncio
    async def test_cancel_workflow(self):
        """Test cancelling a workflow."""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(name="Cancel Test")
        workflow.status = WorkflowStatus.RUNNING

        cancelled = await engine.cancel_workflow(workflow.id)
        assert cancelled is True
        assert workflow.status == WorkflowStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_non_running_workflow(self):
        """Test cancelling non-running workflow."""
        engine = WorkflowEngine()
        workflow = engine.create_workflow(name="Cancel Test")

        cancelled = await engine.cancel_workflow(workflow.id)
        assert cancelled is False
