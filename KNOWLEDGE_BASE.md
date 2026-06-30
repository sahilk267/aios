# AIOS - Knowledge Base

## Project Overview

AIOS (Artificial Intelligence Operating System) is an open-source, self-evolving AI engineering platform. It is designed to build itself continuously through safe iterations.

## Core Principles

1. **Never create throwaway code** - Everything must be modular
2. **Everything must be documented** - No undocumented code
3. **Everything must be versioned** - Git for all code
4. **Everything must be testable** - Tests required for all modules
5. **Everything must be replaceable** - Plugin architecture
6. **Everything must be observable** - Logging, metrics, tracing
7. **Everything must be recoverable** - Backups, rollback capability
8. **Everything must be open source** - No proprietary dependencies
9. **Everything must support local execution** - No cloud requirements
10. **Never require paid APIs** - Free models only

## Architecture Summary

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLite (primary), Qdrant (vector), NetworkX (graph)
- **AI Providers**: Ollama, OpenRouter (free), LiteLLM, LM Studio, vLLM
- **Task Queue**: asyncio with Redis (optional caching)

### Frontend
- **Framework**: Tauri + React + TypeScript
- **State Management**: Zustand
- **Styling**: Tailwind CSS

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Prometheus + Grafana + Loki
- **CI/CD**: GitHub Actions
- **Version Control**: Git + Gitea (self-hosted option)

## Module Index

### Infrastructure Modules
- `backend/aios/core/config.py` - Configuration management
- `backend/aios/core/logging.py` - Structured logging
- `backend/aios/core/events.py` - Lifecycle events
- `backend/aios/core/security.py` - Security utilities
- `backend/aios/database/connection.py` - Database connection

### Engine Modules
- `backend/aios/engine/agent_engine.py` - Agent lifecycle
- `backend/aios/engine/workflow_engine.py` - Workflow execution
- `backend/aios/engine/task_scheduler.py` - Task scheduling
- `backend/aios/engine/dependency_resolver.py` - DAG resolution

### Agent Modules
- `backend/aios/agents/base.py` - BaseAgent class
- `backend/aios/agents/planner.py` - Planner agent
- `backend//architect.py` - Architect agent
- `backend/aios/agents/backend_engineer.py` - Backend Engineer agent
- `backend/aios/agents/reviewer.py` - Reviewer agent
- `backend/aios/agents/qa_engineer.py` - QA Engineer agent

### Provider Modules
- `backend/aios/providers/base.py` - BaseProvider class
- `backend/aios/providers/ollama.py` - Ollama provider
- `backend/aios/providers/openrouter.py` - OpenRouter provider
- `backend/aios/providers/litellm.py` - LiteLLM provider

### Memory Modules
- `backend/aios/memory/short_term.py` - Short-term memory
- `backend/aios/memory/long_term.py` - Long-term memory
- `backend/aios/memory/vector.py` - Vector memory (Qdrant)
- `backend/aios/memory/graph.py` - Graph memory (NetworkX)

### Knowledge Modules
- `backend/aios/knowledge/indexer.py` - Document indexing
- `backend/aios/knowledge/embedder.py` - Text embedding
- `backend/aios/knowledge/search.py` - Semantic search

### Indexing System
- `backend/aios/knowledge/indexer.py` - Main indexing engine
- `backend/aios/knowledge/embedder.py` - Embedding generation
- `scripts/file_watcher.py` - File change watcher
- `scripts/auto_index.py` - Automatic indexing

## Key Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.100+ | Web framework |
| SQLAlchemy | 2.0+ | ORM |
| Alembic | 1.12+ | Migrations |
| Qdrant Client | 1.6+ | Vector store |
| NetworkX | 3.1+ | Graph store |
| Pydantic | 2.0+ | Validation |
| Uvicorn | 0.23+ | ASGI server |
| Structlog | 23.0+ | Logging |
| Ruff | 0.1+ | Linting |
| Pytest | 7.0+ | Testing |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| AIOS_ENV | development | Environment name |
| AIOS_DB_PATH | data/sqlite/aios.db | SQLite database path |
| AIOS_QDRANT_PATH | data/qdrant | Qdrant storage path |
| AIOS_LOG_LEVEL | INFO | Logging level |
| AIOS_DEBUG | false | Debug mode |
| AIOS_SECRET_KEY | auto-generated | Secret key for JWT |
| AIOS_OLLAMA_URL | http://localhost:11434 | Ollama API URL |
| AIOS_OPENROUTER_KEY | None | OpenRouter API key |

## API Endpoints

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/detailed` - Detailed health check

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Agents
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents/{id}` - Get agent
- `POST /api/v1/agents/{id}/execute` - Execute agent task

### Workflows
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow
- `POST /api/v1/workflows/{id}/execute` - Execute workflow

### Memory
- `GET /api/v1/memory/search` - Search memory
- `POST /api/v1/memory` - Store memory

### Knowledge
- `GET /api/v1/knowledge/search` - Search knowledge
- `POST /api/v1/knowledge/index` - Index document

## Glossary

| Term | Definition |
|------|-----------|
| Agent | An AI role with specific capabilities and responsibilities |
| Workflow | A directed acyclic graph of tasks |
| Task | A unit of work assigned to an agent |
| Provider | An AI model service (Ollama, OpenRouter, etc.) |
| Memory | Persistent storage for agent context |
| Knowledge | Indexed information from various sources |
| Plugin | An extensible component that adds functionality |
| Indexing | The process of creating embeddings for retrieval |
