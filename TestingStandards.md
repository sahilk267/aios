# AIOS - Testing Standards

## 1. Overview

This document defines the testing standards and strategy for the AIOS project. Testing is integral to development, not an afterthought.

## 2. Testing Philosophy

1. **Test-Driven Development**: Write tests before or alongside code
2. **Pyramid Strategy**: Many unit tests, fewer integration tests, fewest E2E tests
3. **Fast Feedback**: Tests should run quickly and provide clear failure messages
4. **Deterministic**: Tests should not depend on timing or external state
5. **Isolated**: Tests should not affect each other

## 3. Test Pyramid

```
            ╱╲
           ╱  ╲
          ╱ E2E╲              5% - Full system tests
         ╱──────╲                Critical user journeys
        ╱        ╲
       ╱ Integration╲        15% - Service boundaries
      ╱──────────────╲          API, database, providers
     ╱                ╲
    ╱    Unit Tests     ╲    80% - Individual functions
   ╱────────────────────╲      Classes, methods, logic
```

## 4. Test Types

### 4.1 Unit Tests

**Location**: `backend/tests/unit/`

**Framework**: pytest + pytest-asyncio

**Coverage Target**: >80% line coverage, >90% for critical paths

**Standards**:
```python
# test_agent_engine.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from aios.engine.agent_engine import AgentEngine
from aios.models.agent import Agent, AgentRole


class TestAgentEngine:
    """Tests for AgentEngine class."""

    @pytest.fixture
    def mock_provider_router(self):
        router = MagicMock()
        router.get_provider = AsyncMock()
        return router

    @pytest.fixture
    def mock_event_bus(self):
        bus = MagicMock()
        bus.publish = AsyncMock()
        return bus

    @pytest.fixture
    def agent_engine(self, mock_provider_router, mock_event_bus):
        return AgentEngine(
            provider_router=mock_provider_router,
            event_bus=mock_event_bus,
        )

    @pytest.mark.asyncio
    async def test_create_agent_success(
        self, agent_engine, mock_provider_router
    ):
        """Test successful agent creation."""
        # Arrange
        mock_provider_router.get_provider.return_value = MagicMock()

        # Act
        agent = await agent_engine.create_agent(
            role=AgentRole.PLANNER,
            name="test-planner",
        )

        # Assert
        assert agent.role == AgentRole.PLANNER
        assert agent.name == "test-planner"
        assert agent.status == "idle"

    @pytest.mark.asyncio
    async def test_create_agent_invalid_role(self, agent_engine):
        """Test agent creation with invalid role raises error."""
        with pytest.raises(InvalidAgentRoleError):
            await agent_engine.create_agent(
                role="invalid_role",
                name="test",
            )

    @pytest.mark.asyncio
    async def test_execute_task_timeout(
        self, agent_engine, mock_provider_router
    ):
        """Test task execution timeout handling."""
        # Arrange
        mock_provider = AsyncMock()
        mock_provider.chat_completion = AsyncMock(
            side_effect=asyncio.TimeoutError()
        )
        mock_provider_router.get_provider.return_value = mock_provider
        agent = await agent_engine.create_agent(role=AgentRole.PLANNER)

        # Act & Assert
        with pytest.raises(TaskTimeoutError):
            await agent_engine.execute_task(
                agent=agent,
                task=MockTask(),
                timeout=0.1,
            )
```

**Naming Convention**:
- File: `test_<module_name>.py`
- Class: `Test<ClassName>`
- Method: `test_<action>_<expected_outcome>`

### 4.2 Integration Tests

**Location**: `backend/tests/integration/`

**Framework**: pytest + pytest-asyncio + testcontainers (for services)

**Standards**:
```python
# test_agent_workflow_integration.py
import pytest
from aios.engine.workflow_engine import WorkflowEngine
from aios.database.connection import get_session


class TestAgentWorkflowIntegration:
    """Integration tests for agent workflow execution."""

    @pytest.fixture
    async def db_session(self):
        """Provide a test database session."""
        async with get_session() as session:
            yield session
            await session.rollback()

    @pytest.fixture
    async def workflow_engine(self, db_session):
        """Provide a configured workflow engine."""
        return WorkflowEngine(
            session=db_session,
            provider_router=TestProviderRouter(),
        )

    @pytest.mark.asyncio
    async def test_full_workflow_execution(
        self, workflow_engine, db_session
    ):
        """Test complete workflow from creation to completion."""
        # Arrange
        workflow = await workflow_engine.create_workflow(
            name="test-workflow",
            tasks=[
                TaskDef(type="plan", agent_role="planner"),
                TaskDef(type="implement", agent_role="backend", depends_on=["plan"]),
            ],
        )

        # Act
        result = await workflow_engine.execute(workflow.id)

        # Assert
        assert result.status == "completed"
        assert len(result.task_results) == 2
        assert all(r.status == "success" for r in result.task_results)

    @pytest.mark.asyncio
    async def test_workflow_with_failed_task(
        self, workflow_engine, db_session
    ):
        """Test workflow handles task failure correctly."""
        # Arrange
        workflow = await workflow_engine.create_workflow(
            name="failing-workflow",
            tasks=[
                TaskDef(type="plan", agent_role="planner"),
                TaskDef(
                    type="implement",
                    agent_role="backend",
                    should_fail=True,  # Test flag
                ),
            ],
        )

        # Act
        result = await workflow_engine.execute(workflow.id)

        # Assert
        assert result.status == "failed"
        assert result.task_results[1].error is not None
```

### 4.3 End-to-End Tests

**Location**: `backend/tests/e2e/`

**Framework**: pytest + Playwright (for UI) + httpx (for API)

**Standards**:
```python
# test_first_project_e2e.py
import pytest
from playwright.async_api import Page


class TestFirstProjectE2E:
    """End-to-end test for first project creation flow."""

    @pytest.mark.asyncio
    async def test_complete_first_project_flow(
        self, page: Page, test_server
    ):
        """Test the complete first project setup flow."""
        # Navigate to app
        await page.goto("http://localhost:3000")

        # Verify dashboard loads
        await page.wait_for_selector("[data-testid='dashboard']")

        # Create new project
        await page.click("[data-testid='new-project-btn']")
        await page.fill("[data-testid='project-name']", "Test Project")
        await page.fill("[data-testid='project-path']", "/tmp/test-project")
        await page.click("[data-testid='create-project-btn']")

        # Verify project created
        await page.wait_for_selector("[data-testid='project-list']")
        project_card = page.locator(
            "[data-testid='project-card']",
            has_text="Test Project"
        )
        assert await project_card.is_visible()

        # Create an agent
        await page.click("[data-testid='agents-tab']")
        await page.click("[data-testid='new-agent-btn']")
        await page.select_option(
            "[data-testid='agent-role']", "planner"
        )
        await page.click("[data-testid='create-agent-btn']")

        # Verify agent created
        agent_card = page.locator(
            "[data-testid='agent-card']",
            has_text="Planner"
        )
        assert await agent_card.is_visible()
```

### 4.4 Frontend Tests

**Location**: `frontend/src/__tests__/`

**Framework**: Vitest + React Testing Library

**Standards**:
```typescript
// AgentCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from '../components/agents/AgentCard';
import { Agent, AgentStatus } from '../types/agent';

const mockAgent: Agent = {
  id: '1',
  name: 'Test Planner',
  role: 'planner',
  status: AgentStatus.Idle,
  modelProvider: 'ollama',
  modelName: 'qwen2.5',
};

describe('AgentCard', () => {
  it('renders agent name and role', () => {
    render(<AgentCard agent={mockAgent} onExecute={jest.fn()} />);

    expect(screen.getByText('Test Planner')).toBeInTheDocument();
    expect(screen.getByText('planner')).toBeInTheDocument();
  });

  it('shows idle status badge', () => {
    render(<AgentCard agent={mockAgent} onExecute={jest.fn()} />);

    const badge = screen.getByTestId('status-badge');
    expect(badge).toHaveTextContent('idle');
    expect(badge).toHaveClass('bg-green-500');
  });

  it('calls onExecute when button clicked', () => {
    const onExecute = jest.fn();
    render(<AgentCard agent={mockAgent} onExecute={onExecute} />);

    fireEvent.click(screen.getByTestId('execute-btn'));

    expect(onExecute).toHaveBeenCalledWith('1');
  });

  it('disables execute button when agent is running', () => {
    const runningAgent = { ...mockAgent, status: AgentStatus.Running };
    render(<AgentCard agent={runningAgent} onExecute={jest.fn()} />);

    const button = screen.getByTestId('execute-btn');
    expect(button).toBeDisabled();
  });
});
```

## 5. Test Fixtures

### 5.1 Shared Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_ollama_provider():
    """Mock Ollama provider for testing."""
    provider = AsyncMock()
    provider.list_models = AsyncMock(
        return_value=[
            Model(name="qwen2.5", size=4661224676),
            Model(name="deepseek-coder-v2", size=1649864240),
        ]
    )
    provider.chat_completion = AsyncMock(
        return_value=Response(
            content="Test response",
            usage=TokenUsage(prompt=10, completion=5, total=15),
        )
    )
    return provider


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    return Agent(
        id="test-agent-1",
        role=AgentRole.PLANNER,
        name="Test Planner",
        model_provider="ollama",
        model_name="qwen2.5",
    )


@pytest.fixture
def sample_workflow():
    """Sample workflow for testing."""
    return Workflow(
        id="test-workflow-1",
        name="Test Workflow",
        tasks=[
            Task(
                id="task-1",
                type="plan",
                agent_role="planner",
                dependencies=[],
            ),
            Task(
                id="task-2",
                type="implement",
                agent_role="backend",
                dependencies=["task-1"],
            ),
        ],
    )
```

### 5.2 Test Data Factories

```python
# tests/factories.py
import factory
from aios.models.agent import Agent, AgentRole


class AgentFactory(factory.Factory):
    class Meta:
        model = Agent

    id = factory.Sequence(lambda n: f"agent-{n}")
    role = AgentRole.PLANNER
    name = factory.LazyAttribute(lambda o: f"{o.role.value}-agent")
    model_provider = "ollama"
    model_name = "qwen2.5"
    status = "idle"
```

## 6. Test Configuration

### 6.1 pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
asyncio_mode = "auto"
addopts = [
    "--strict-markers",
    "--strict-config",
    "-v",
    "--tb=short",
    "--cov=aios",
    "--cov-report=term-missing",
    "--cov-fail-under=80",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
    "e2e: marks end-to-end tests",
    "security: marks security-related tests",
]
```

### 6.2 Test Environment

```python
# .env.test
DATABASE_URL=sqlite+aiosqlite:///./test.db
QDRANT_PATH=./test_qdrant
LOG_LEVEL=DEBUG
TESTING=true
```

## 7. Coverage Requirements

| Component | Line Coverage | Branch Coverage |
|-----------|--------------|-----------------|
| Core engine | >90% | >85% |
| Services | >85% | >80% |
| API layer | >80% | >75% |
| Models/Schemas | >90% | N/A |
| Utilities | >90% | >85% |
| Overall | >80% | >75% |

## 8. Test Execution

### 8.1 Local Development

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m "not integration and not e2e"

# Run specific test file
pytest tests/unit/test_agent_engine.py

# Run with coverage
pytest --cov --cov-report=html

# Run in watch mode
ptw  # pytest-watch
```

### 8.2 CI Pipeline

```yaml
# .github/workflows/test.yml
- name: Run unit tests
  run: pytest -m "unit" --cov --cov-report=xml

- name: Run integration tests
  run: pytest -m "integration"

- name: Run E2E tests
  run: pytest -m "e2e"

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## 9. Test Review Checklist

- [ ] Tests cover happy path
- [ ] Tests cover error cases
- [ ] Tests cover edge cases (empty input, max values, etc.)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests are isolated (no shared state)
- [ ] Test names clearly describe the scenario
- [ ] Mocking is appropriate (not over-mocked)
- [ ] Async tests use proper async patterns
- [ ] No test depends on another test
- [ ] Coverage meets targets
