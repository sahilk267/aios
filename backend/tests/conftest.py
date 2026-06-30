"""AIOS Test Configuration and Fixtures."""

import pytest
import pytest_asyncio
from typing import AsyncGenerator


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "path": "/tmp/test-project",
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "name": "Test Agent",
        "role": "planner",
        "description": "A test agent",
        "provider": "ollama",
        "model": "llama3",
        "config": {},
    }


@pytest.fixture
def sample_workflow_data():
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow",
        "tasks": [
            {
                "id": "task-1",
                "type": "plan",
                "agent_role": "planner",
                "input": {"query": "test"},
                "depends_on": [],
            }
        ],
        "dependencies": {},
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "type": "decision",
        "content": "This is a test memory",
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_knowledge_data():
    """Sample knowledge data for testing."""
    return {
        "source": "test.md",
        "content": "This is test knowledge content",
        "metadata": {"author": "test"},
    }
