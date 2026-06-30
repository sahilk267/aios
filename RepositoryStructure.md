# AIOS - Repository Structure

## 1. Overview

This document defines the complete repository structure for AIOS. The project uses a monorepo approach with clear separation between frontend (Tauri/React), backend (Python), and shared components.

## 2. Directory Tree

```
aios/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Main CI pipeline
│   │   ├── release.yml               # Release automation
│   │   ├── security-scan.yml         # Security scanning
│   │   └── docs.yml                  # Documentation deployment
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── plugin_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS
├── .roomodes/                         # Roo Code integration config
├── docs/
│   ├── source/
│   │   ├── conf.py
│   │   ├── index.rst
│   │   ├── getting_started/
│   │   │   ├── installation.rst
│   │   │   ├── quickstart.rst
│   │   │   ├── configuration.rst
│   │   │   └── ide_integration.rst
│   │   ├── user_guide/
│   │   │   ├── agents.rst
│   │   │   ├── workflows.rst
│   │   │   ├── memory.rst
│   │   │   ├── knowledge.rst
│   │   │   ├── plugins.rst
│   │   │   └── security.rst
│   │   ├── developer_guide/
│   │   │   ├── architecture.rst
│   │   │   ├── contributing.rst
│   │   │   ├── plugin_development.rst
│   │   │   ├── provider_development.rst
│   │   │   └── api_reference.rst
│   │   ├── tutorials/
│   │   │   ├── first_project.rst
│   │   │   ├── custom_agent.rst
│   │   │   ├── custom_plugin.rst
│   │   │   └── team_workflows.rst
│   │   └── api/
│   │       ├── rest_api.rst
│   │       ├── websocket_events.rst
│   │       └── mcp_protocol.rst
│   ├── assets/
│   │   ├── images/
│   │   ├── diagrams/
│   │   └── videos/
│   └── mkdocs.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Dialog.tsx
│   │   │   │   ├── Dropdown.tsx
│   │   │   │   ├── Icon.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Loading.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Tabs.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   └── Tooltip.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── AgentStatusCard.tsx
│   │   │   │   ├── HealthOverview.tsx
│   │   │   │   ├── MetricsChart.tsx
│   │   │   │   ├── RecentActivity.tsx
│   │   │   │   └── SystemStats.tsx
│   │   │   ├── agents/
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   ├── AgentCreator.tsx
│   │   │   │   ├── AgentDetail.tsx
│   │   │   │   ├── AgentList.tsx
│   │   │   │   ├── AgentLogViewer.tsx
│   │   │   │   └── AgentStatusBadge.tsx
│   │   │   ├── workflows/
│   │   │   │   ├── WorkflowDesigner.tsx
│   │   │   │   ├── WorkflowList.tsx
│   │   │   │   ├── WorkflowRunner.tsx
│   │   │   │   ├── WorkflowStatus.tsx
│   │   │   │   ├── TaskNode.tsx
│   │   │   │   └── ApprovalGate.tsx
│   │   │   ├── memory/
│   │   │   │   ├── MemoryBrowser.tsx
│   │   │   │   ├── MemoryEntry.tsx
│   │   │   │   ├── MemorySearch.tsx
│   │   │   │   └── MemoryTypeFilter.tsx
│   │   │   ├── knowledge/
│   │   │   │   ├── KnowledgeGraph.tsx
│   │   │   │   ├── KnowledgeSearch.tsx
│   │   │   │   ├── KnowledgeSource.tsx
│   │   │   │   └── DocumentViewer.tsx
│   │   │   ├── plugins/
│   │   │   │   ├── PluginCard.tsx
│   │   │   │   ├── PluginDetail.tsx
│   │   │   │   ├── PluginInstall.tsx
│   │   │   │   └── PluginList.tsx
│   │   │   ├── providers/
│   │   │   │   ├── ProviderCard.tsx
│   │   │   │   ├── ProviderConfig.tsx
│   │   │   │   ├── ProviderStatus.tsx
│   │   │   │   └── ModelSelector.tsx
│   │   │   ├── settings/
│   │   │   │   ├── GeneralSettings.tsx
│   │   │   │   ├── ProviderSettings.tsx
│   │   │   │   ├── SecuritySettings.tsx
│   │   │   │   ├── PluginSettings.tsx
│   │   │   │   └── IDESettings.tsx
│   │   │   └── security/
│   │   │       ├── AuditLog.tsx
│   │   │       ├── SecretManager.tsx
│   │   │       └── AccessControl.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── Agents.tsx
│   │   │   ├── Workflows.tsx
│   │   │   ├── Memory.tsx
│   │   │   ├── Knowledge.tsx
│   │   │   ├── Plugins.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── Security.tsx
│   │   ├── hooks/
│   │   │   ├── useApi.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAuth.ts
│   │   │   ├── useTheme.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── services/
│   │   │   ├── apiClient.ts
│   │   │   ├── websocketClient.ts
│   │   │   ├── authService.ts
│   │   │   └── pluginService.ts
│   │   ├── stores/
│   │   │   ├── agentStore.ts
│   │   │   ├── projectStore.ts
│   │   │   ├── workflowStore.ts
│   │   │   ├── memoryStore.ts
│   │   │   ├── notificationStore.ts
│   │   │   └── settingsStore.ts
│   │   ├── types/
│   │   │   ├── agent.ts
│   │   │   ├── workflow.ts
│   │   │   ├── memory.ts
│   │   │   ├── knowledge.ts
│   │   │   ├── plugin.ts
│   │   │   ├── provider.ts
│   │   │   ├── project.ts
│   │   │   └── websocket.ts
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   ├── validation.ts
│   │   │   ├── constants.ts
│   │   │   └── helpers.ts
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   ├── variables.css
│   │   │   └── tailwind.config.js
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── src-tauri/
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── commands/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── agent_commands.rs
│   │   │   │   ├── project_commands.rs
│   │   │   │   ├── provider_commands.rs
│   │   │   │   ├── system_commands.rs
│   │   │   │   └── file_commands.rs
│   │   │   ├── ipc/
│   │   │   │   ├── mod.rs
│   │   │   │   ├── event_bus.rs
│   │   │   │   └── state.rs
│   │   │   ├── config/
│   │   │   │   ├── mod.rs
│   │   │   │   └── tauri.conf.json
│   │   │   └── utils/
│   │   │       ├── mod.rs
│   │   │       └── file_system.rs
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── backend/
│   ├── aios/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py               # Configuration management
│   │   │   ├── events.py               # Lifecycle events
│   │   │   ├── exceptions.py           # Custom exceptions
│   │   │   ├── security.py             # Security utilities
│   │   │   └── logging.py              # Structured logging
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                 # Dependency injection
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py           # API router aggregation
│   │   │   │   ├── projects.py         # Project endpoints
│   │   │   │   ├── agents.py           # Agent endpoints
│   │   │   │   ├── workflows.py       # Workflow endpoints
│   │   │   │   ├── memory.py           # Memory endpoints
│   │   │   │   ├── knowledge.py        # Knowledge endpoints
│   │   │   │   ├── plugins.py          # Plugin endpoints
│   │   │   │   ├── providers.py        # Provider endpoints
│   │   │   │   ├── security.py         # Security endpoints
│   │   │   │   └── system.py           # System endpoints
│   │   │   └── websocket/
│   │   │       ├── __init__.py
│   │   │       ├── router.py
│   │   │       ├── handlers.py
│   │   │       └── events.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── agent.py
│   │   │   ├── workflow.py
│   │   │   ├── task.py
│   │   │   ├── memory.py
│   │   │   ├── knowledge.py
│   │   │   ├── plugin.py
│   │   │   ├── provider.py
│   │   │   ├── audit.py
│   │   │   └── base.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── agent.py
│   │   │   ├── workflow.py
│   │   │   ├── task.py
│   │   │   ├── memory.py
│   │   │   ├── knowledge.py
│   │   │   ├── plugin.py
│   │   │   ├── provider.py
│   │   │   └── common.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py
│   │   │   ├── agent_service.py
│   │   │   ├── workflow_service.py
│   │   │   ├── memory_service.py
│   │   │   ├── knowledge_service.py
│   │   │   ├── plugin_service.py
│   │   │   ├── provider_service.py
│   │   │   ├── security_service.py
│   │   │   └── system_service.py
│   │   ├── engine/
│   │   │   ├── __init__.py
│   │   │   ├── agent_engine.py         # Agent lifecycle management
│   │   │   ├── workflow_engine.py      # Workflow execution
│   │   │   ├── task_scheduler.py       # Task scheduling
│   │   │   ├── dependency_resolver.py  # DAG resolution
│   │   │   └── parallel_executor.py    # Concurrent execution
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # BaseAgent class
│   │   │   ├── registry.py             # Agent role registry
│   │   │   ├── planner.py              # Planner agent
│   │   │   ├── product_manager.py      # Product Manager agent
│   │   │   ├── architect.py            # Architect agent
│   │   │   ├── backend_engineer.py     # Backend Engineer agent
│   │   │   ├── frontend_engineer.py    # Frontend Engineer agent
│   │   │   ├── database_engineer.py    # Database Engineer agent
│   │   │   ├── security_engineer.py    # Security Engineer agent
│   │   │   ├── qa_engineer.py          # QA Engineer agent
│   │   │   ├── devops_engineer.py      # DevOps Engineer agent
│   │   │   ├── documentation_engineer.py # Documentation Engineer agent
│   │   │   ├── research_agent.py       # Research Agent
│   │   │   ├── reviewer.py             # Reviewer agent
│   │   │   └── optimization_agent.py   # Optimization Agent
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # BaseProvider class
│   │   │   ├── registry.py             # Provider registry
│   │   │   ├── router.py               # Task routing
│   │   │   ├── ollama.py               # Ollama provider
│   │   │   ├── openrouter.py           # OpenRouter provider
│   │   │   ├── litellm.py              # LiteLLM provider
│   │   │   ├── openai_compatible.py    # OpenAI-compatible provider
│   │   │   ├── lm_studio.py            # LM Studio provider
│   │   │   ├── vllm.py                 # vLLM provider
│   │   │   └── huggingface.py          # HuggingFace provider
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base memory store
│   │   │   ├── short_term.py           # Short-term memory
│   │   │   ├── long_term.py            # Long-term memory
│   │   │   ├── vector.py               # Vector memory (Qdrant)
│   │   │   ├── graph.py                # Graph memory (NetworkX)
│   │   │   ├── decision.py             # Decision memory
│   │   │   ├── project.py              # Project memory
│   │   │   ├── conversation.py         # Conversation memory
│   │   │   ├── architecture.py         # Architecture memory
│   │   │   └── learning.py             # Learning memory
│   │   ├── knowledge/
│   │   │   ├── __init__.py
│   │   │   ├── indexer.py              # Document indexing
│   │   │   ├── embedder.py             # Text embedding
│   │   │   ├── search.py               # Semantic search
│   │   │   ├── graph_builder.py        # Knowledge graph
│   │   │   ├── freshness.py            # Freshness monitoring
│   │   │   └── connectors/
│   │   │       ├── __init__.py
│   │   │       ├── git_connector.py
│   │   │       ├── file_connector.py
│   │   │       ├── web_connector.py
│   │   │       └── api_connector.py
│   │   ├── plugins/
│   │   │   ├── __init__.py
│   │   │   ├── manager.py              # Plugin lifecycle
│   │   │   ├── loader.py               # Plugin loading
│   │   │   ├── sandbox.py              # Plugin isolation
│   │   │   ├── validator.py            # Plugin validation
│   │   │   ├── api.py                  # Plugin API interface
│   │   │   └── builtin/
│   │   │       ├── __init__.py
│   │   │       ├── git_plugin.py
│   │   │       ├── docker_plugin.py
│   │   │       └── test_plugin.py
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 # Authentication
│   │   │   ├── rbac.py                 # Role-based access
│   │   │   ├── secrets.py              # Secret management
│   │   │   ├── audit.py                # Audit logging
│   │   │   └── encryption.py           # Encryption utilities
│   │   ├── observability/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py              # Structured logging
│   │   │   ├── metrics.py              # Metrics collection
│   │   │   ├── tracing.py              # Distributed tracing
│   │   │   ├── health.py               # Health checks
│   │   │   └── alerts.py               # Alerting
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # BaseTool class
│   │   │   ├── registry.py             # Tool registry
│   │   │   ├── git_tool.py
│   │   │   ├── docker_tool.py
│   │   │   ├── shell_tool.py
│   │   │   ├── file_tool.py
│   │   │   ├── web_tool.py
│   │   │   ├── test_tool.py
│   │   │   ├── security_tool.py
│   │   │   └── mcp_tool.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py           # Database connection
│   │   │   ├── migrations/             # Alembic migrations
│   │   │   │   ├── env.py
│   │   │   │   └── versions/
│   │   │   ├── repository.py           # Repository pattern
│   │   │   └── init_db.py              # Database initialization
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── text.py                 # Text processing
│   │       ├── crypto.py               # Cryptography
│   │       ├── async_utils.py          # Async helpers
│   │       └── validators.py           # Input validation
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_config.py
│   │   │   ├── test_agent_engine.py
│   │   │   ├── test_workflow_engine.py
│   │   │   ├── test_memory_service.py
│   │   │   ├── test_knowledge_service.py
│   │   │   ├── test_plugin_manager.py
│   │   │   ├── test_provider_router.py
│   │   │   └── test_security.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_agent_workflow.py
│   │   │   ├── test_memory_flow.py
│   │   │   ├── test_knowledge_index.py
│   │   │   └── test_plugin_lifecycle.py
│   │   ├── e2e/
│   │   │   ├── __init__.py
│   │   │   ├── test_full_workflow.py
│   │   │   └── test_desktop_app.py
│   │   └── fixtures/
│   │       ├── __init__.py
│   │       ├── agents.py
│   │       ├── projects.py
│   │       └── workflows.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── plugins/
│   ├── agent-plugins/
│   │   └── README.md
│   ├── tool-plugins/
│   │   └── README.md
│   ├── provider-plugins/
│   │   └── README.md
│   └── workflow-plugins/
│       └── README.md
├── scripts/
│   ├── setup.sh                        # Initial setup script
│   ├── dev.sh                          # Development startup
│   ├── build.sh                        # Production build
│   ├── test.sh                         # Test runner
│   ├── lint.sh                         # Linting
│   └── release.sh                      # Release packaging
├── config/
│   ├── default.toml                    # Default configuration
│   ├── agents/
│   │   ├── planner.toml
│   │   ├── architect.toml
│   │   ├── backend_engineer.toml
│   │   └── ...
│   └── workflows/
│       ├── feature_impl.toml
│       ├── bug_fix.toml
│       └── ...
├── data/                               # Runtime data (gitignored)
│   ├── sqlite/
│   ├── qdrant/
│   ├── logs/
│   └── cache/
├── .gitignore
├── .gitattributes
├── LICENSE                             # Apache-2.0 or MIT
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── CODE_OF_CONDUCT.md
└── pyproject.toml                      # Root project config
```

## 3. Key Design Decisions

### 3.1 Monorepo Structure

- **Single repository** for frontend, backend, plugins, and docs
- **Clear boundaries** between components via directory structure
- **Shared types** via generated TypeScript/Python type definitions
- **Unified CI/CD** pipeline for all components

### 3.2 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files (Python) | snake_case | `agent_service.py` |
| Files (React) | PascalCase (components) | `AgentCard.tsx` |
| Classes | PascalCase | `AgentEngine` |
| Functions/Methods | snake_case | `execute_task` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Database tables | snake_case_plural | `agent_configs` |
| API endpoints | kebab-case | `/api/v1/agent-configs` |
| Events | dot-separated | `agent.status.changed` |
| Environment variables | UPPER_SNAKE_CASE | `AIOS_DB_PATH` |

### 3.3 Branch Strategy

```
main (protected)
├── develop (integration)
│   ├── feature/*
│   ├── bugfix/*
│   └── plugin/*
├── release/*
└── hotfix/*
```

### 3.4 Code Organization Principles

1. **Feature-based organization** within engine components
2. **Dependency direction**: API → Services → Engine → Models → Database
3. **Plugin isolation**: Plugins never import from each other
4. **Provider abstraction**: All providers implement common interface
5. **Schema separation**: Database models ≠ API schemas ≠ Internal models

## 4. Configuration Files

### 4.1 Root Configuration

```toml
# pyproject.toml
[project]
name = "aios"
version = "0.1.0"
description = "Artificial Intelligence Operating System"
requires-python = ">=3.11"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.pytest.ini_options]
testpaths = ["backend/tests"]
```

### 4.2 Frontend Configuration

```json
// frontend/package.json
{
  "name": "aios-frontend",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "tauri": "tauri",
    "tauri-dev": "tauri dev",
    "tauri-build": "tauri build"
  }
}
```

## 5. Git Ignore Patterns

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Frontend
node_modules/
dist/
dist-tauri/

# Data
data/sqlite/*.db
data/qdrant/
data/logs/
data/cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets
*.env
*.pem
*.key
secrets/
