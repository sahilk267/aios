# AIOS - Coding Standards

## 1. Overview

This document defines the coding standards for the AIOS project. All contributors must follow these standards to ensure code quality, consistency, and maintainability.

## 2. General Principles

1. **Readability over cleverness**: Code should be obvious, not tricky
2. **Explicit over implicit**: Clear type annotations, explicit error handling
3. **Simplicity**: Prefer simple solutions; avoid premature optimization
4. **Consistency**: Follow established patterns in the codebase
5. **Testability**: Design code to be easily testable

## 3. Python Standards

### 3.1 Version and Tooling

- **Python Version**: 3.11+
- **Type Checking**: mypy in strict mode
- **Linting**: Ruff (replaces flake8, isort, pyflakes)
- **Formatting**: Ruff (replaces black)
- **Import Sorting**: Ruff (replaces isort)

### 3.2 Code Style

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # bugbear
    "C4",  # comprehensions
    "UP",  # pyupgrade
    "SIM", # simplify
    "S",   # bandit security
    "RUF", # ruff-specific
]

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

### 3.3 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Module | snake_case | `agent_service.py` |
| Package | snake_case | `aios.engine` |
| Class | PascalCase | `AgentEngine` |
| Function | snake_case | `execute_task` |
| Method | snake_case | `execute_task` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Variable | snake_case | `task_result` |
| Private | _leading_underscore | `_internal_state` |
| TypeVar | PascalCase or _co/_contra suffix | `T`, `T_co` |
| Protocol | PascalCase | `AgentProtocol` |
| Enum | PascalCase | `AgentStatus` |
| Enum member | UPPER_SNAKE_CASE | `AgentStatus.RUNNING` |

### 3.4 Type Annotations

All functions must have complete type annotations:

```python
# Good
async def execute_task(
    self,
    task: Task,
    agent: Agent,
    *,
    timeout: float = 30.0,
    retries: int = 3,
) -> TaskResult:
    ...

# Bad
async def execute_task(self, task, agent, timeout=30, retries=3):
    ...
```

### 3.5 Docstrings

Use Google-style docstrings for all public modules, classes, and functions:

```python
class AgentEngine:
    """Manages the lifecycle of AI agents.

    The AgentEngine is responsible for creating, executing, and monitoring
    agents. It coordinates with the ProviderRouter for model access and
    the MemoryService for context retrieval.

    Attributes:
        registry: Agent role registry for looking up agent definitions.
        provider_router: Router for selecting appropriate model providers.
        event_bus: Event bus for publishing agent lifecycle events.

    Example:
        engine = AgentEngine(provider_router, event_bus)
        agent = await engine.create_agent(role=AgentRole.PLANNER)
    """

    async def execute_task(
        self,
        task: Task,
        agent: Agent,
        *,
        timeout: float = 30.0,
    ) -> TaskResult:
        """Executes a task using the specified agent.

        Args:
            task: The task to execute with input parameters.
            agent: The agent to execute the task.
            timeout: Maximum execution time in seconds.

        Returns:
            The task result with output and metadata.

        Raises:
            TaskTimeoutError: If execution exceeds timeout.
            AgentError: If agent encounters an error.
        """
        ...
```

### 3.6 Import Ordering

```python
# Standard library
import asyncio
import logging
from typing import Optional
from datetime import datetime

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Local
from aios.core.config import settings
from aios.models.agent import Agent
from aios.services.memory_service import MemoryService
```

### 3.7 Error Handling

Define custom exceptions and handle errors explicitly:

```python
# Custom exceptions
class AIOSBaseError(Exception):
    """Base exception for AIOS."""

class AgentError(AIOSBaseError):
    """Raised when an agent encounters an error."""

class ProviderError(AIOSBaseError):
    """Raised when a provider fails."""

class WorkflowError(AIOSBaseError):
    """Raised when a workflow fails."""

# Usage
async def execute_task(task: Task) -> TaskResult:
    try:
        result = await agent.execute(task)
    except asyncio.TimeoutError as e:
        raise TaskTimeoutError(f"Task {task.id} timed out") from e
    except ProviderError as e:
        logger.error("Provider failed for task %s: %s", task.id, e)
        raise
    else:
        return result
```

### 3.8 Async Patterns

```python
# Use async/await consistently
async def process_tasks(tasks: list[Task]) -> list[TaskResult]:
    coros = [process_task(task) for task in tasks]
    return await asyncio.gather(*coros, return_exceptions=True)

# Use async context managers
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Use asyncio.TaskGroup for structured concurrency (Python 3.11+)
async def run_parallel(agent_tasks: list[AgentTask]) -> None:
    async with asyncio.TaskGroup() as tg:
        for task in agent_tasks:
            tg.create_task(execute_agent_task(task))
```

### 3.9 Pydantic Models

```python
from pydantic import BaseModel, Field, field_validator

class AgentConfig(BaseModel):
    """Configuration for an agent."""

    role: AgentRole
    model_provider: str = Field(..., min_length=1, max_length=100)
    model_name: str = Field(..., min_length=1, max_length=100)
    max_tokens: int = Field(default=4096, ge=1, le=100000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._/-]+$", v):
            raise ValueError("Invalid model name format")
        return v
```

## 4. TypeScript/React Standards

### 4.1 Tooling

- **TypeScript**: Strict mode enabled
- **Linter**: ESLint with recommended + TypeScript rules
- **Formatter**: Prettier
- **Framework**: React 18+ with hooks

### 4.2 Code Style

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

```json
// .eslintrc
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended"
  ],
  "rules": {
    "no-console": "warn",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "error",
    "react/react-in-jsx-scope": "off"
  }
}
```

### 4.3 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| File (component) | PascalCase | `AgentCard.tsx` |
| File (utility) | camelCase | `formatDate.ts` |
| Component | PascalCase | `AgentCard` |
| Props interface | ComponentName + Props | `AgentCardProps` |
| Hook | use + PascalCase | `useWebSocket` |
| Function | camelCase | `executeTask` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Type | PascalCase | `AgentConfig` |
| Enum | PascalCase | `AgentStatus` |
| Enum member | PascalCase | `AgentStatus.Running` |

### 4.4 Component Patterns

```typescript
// Functional components with explicit types
interface AgentCardProps {
  agent: Agent;
  onExecute: (agentId: string) => void;
  className?: string;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onExecute,
  className,
}) => {
  return (
    <Card className={className}>
      <AgentStatusBadge status={agent.status} />
      <h3>{agent.name}</h3>
      <Button onClick={() => onExecute(agent.id)}>Execute</Button>
    </Card>
  );
};
```

### 4.5 Custom Hooks

```typescript
export const useWebSocket = (url: string) => {
  const [data, setData] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => setData(JSON.parse(event.data));
    ws.onerror = (event) => setError(new Error("WebSocket error"));
    return () => ws.close();
  }, [url]);

  return { data, error };
};
```

### 4.6 State Management

Use Zustand for state management:

```typescript
interface AgentStore {
  agents: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
  fetchAgents: () => Promise<void>;
  selectAgent: (id: string) => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: [],
  selectedAgent: null,
  loading: false,
  error: null,
  fetchAgents: async () => {
    set({ loading: true });
    try {
      const agents = await agentApi.list();
      set({ agents, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  selectAgent: (id) => {
    const agent = get().agents.find((a) => a.id === id) ?? null;
    set({ selectedAgent: agent });
  },
}));
```

## 5. Rust Standards (Tauri)

### 5.1 Tooling

- **Formatter**: rustfmt
- **Linter**: clippy
- **Edition**: Rust 2021

### 5.2 Code Style

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
tab_spaces = 4
```

### 5.3 Error Handling

```rust
// Use thiserror for custom errors
#[derive(Debug, thiserror::Error)]
pub enum AIosError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Provider error: {0}")]
    Provider(String),
}

// Use anyhow for application-level errors
pub fn setup() -> anyhow::Result<()> {
    let config = load_config()?;
    Ok(())
}
```

## 6. Database Standards

### 6.1 Migration Rules

- All schema changes via Alembic migrations
- Migrations must be reversible (down_revision)
- Migration files named: `YYYYMMDD_HHMMSS_description.py`
- Never modify existing migrations
- Test migrations before committing

### 6.2 Query Standards

```python
# Use SQLAlchemy 2.0 async style
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_agent(session: AsyncSession, agent_id: str) -> Agent | None:
    stmt = select(Agent).where(Agent.id == agent_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# Use eager loading for relationships
async def get_agent_with_tasks(session: AsyncSession, agent_id: str) -> Agent | None:
    stmt = (
        select(Agent)
        .where(Agent.id == agent_id)
        .options(selectinload(Agent.tasks))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

## 7. API Design Standards

### 7.1 REST Conventions

| Method | Usage | Example |
|--------|-------|---------|
| GET | Read resource | `GET /api/v1/agents/{id}` |
| POST | Create resource | `POST /api/v1/agents` |
| PUT | Full update | `PUT /api/v1/agents/{id}` |
| PATCH | Partial update | `PATCH /api/v1/agents/{id}` |
| DELETE | Delete resource | `DELETE /api/v1/agents/{id}` |

### 7.2 Response Format

```json
// Success
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  }
}

// Error
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with id '123' not found",
    "details": { ... }
  }
}

// List with pagination
{
  "data": [ ... ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

## 8. Git Standards

### 8.1 Commit Messages

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore, perf, ci, build

Example:
```
feat(agent): add parallel task execution

Implement asyncio-based parallel executor for independent tasks
in workflows. Tasks without dependencies now execute concurrently.

Closes #123
```

### 8.2 Branch Naming

```
feature/agent-parallel-execution
bugfix/memory-leak-session
docs/api-reference-update
refactor/provider-abstraction
```

## 9. Security Standards

1. **Never commit secrets**: Use environment variables or secret management
2. **Validate all inputs**: Pydantic schemas for all API inputs
3. **Sanitize outputs**: Prevent XSS in frontend rendering
4. **Use parameterized queries**: Never string-interpolate SQL
5. **Rate limiting**: Apply to all external-facing endpoints
6. **Dependency scanning**: Run `pip audit` and `npm audit` in CI
7. **Principle of least privilege**: Minimal permissions for plugins and services

## 10. Code Review Checklist

- [ ] Code follows naming conventions
- [ ] All functions have type annotations
- [ ] Public APIs have docstrings
- [ ] Tests cover new functionality
- [ ] No hardcoded secrets or credentials
- [ ] Error handling is explicit
- [ ] No unnecessary complexity
- [ ] Database migrations are included (if applicable)
- [ ] API documentation is updated (if applicable)
- [ ] Performance implications considered
