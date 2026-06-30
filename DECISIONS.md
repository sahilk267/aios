# AIOS - Architecture Decision Records

## ADR-001: Monorepo Structure

**Status**: Accepted

**Context**: Need to decide between monorepo and multi-repo for frontend, backend, plugins, and docs.

**Decision**: Use a monorepo with clear directory boundaries.

**Rationale**:
- Single source of truth for all code
- Easier cross-component changes
- Unified CI/CD pipeline
- Simplified dependency management
- Better developer experience

**Consequences**:
- Larger repository size
- Need for clear boundaries
- Potential for tight coupling if not careful

---

## ADR-002: Python + FastAPI for Backend

**Status**: Accepted

**Context**: Need a backend language/framework that supports async, has good AI/ML ecosystem, and rapid development.

**Decision**: Use Python 3.11+ with FastAPI.

**Rationale**:
- Rich AI/ML ecosystem (LangChain, HuggingFace, etc.)
- Native async support
- Automatic OpenAPI documentation
- High performance with Starlette
- Type hints with Pydantic
- Large community

**Consequences**:
- GIL limitations (mitigated by async)
- Need for type checking (mypy)
- Python packaging complexity

---

## ADR-003: SQLite as Primary Database

**Status**: Accepted

**Context**: Need a database that works locally, requires no setup, and handles moderate data volumes.

**Decision**: Use SQLite as the primary relational database.

**Rationale**:
- Zero configuration
- Embedded (no separate process)
- ACID compliant
- WAL mode for concurrency
- Sufficient for 1-10 users
- Easy backups

**Consequences**:
- Not suitable for high concurrency
- Limited to single machine
- Migration path to PostgreSQL if needed

---

## ADR-004: Qdrant for Vector Storage

**Status**: Accepted

**Context**: Need a vector database for embeddings and semantic search.

**Decision**: Use Qdrant with embedded mode.

**Rationale**:
- Open source
- Embedded mode (no separate process)
- Fast similarity search
- Good Python client
- Supports filtering

**Consequences**:
- Additional dependency
- Need to manage index updates

---

## ADR-005: NetworkX for Graph Storage

**Status**: Accepted

**Context**: Need a graph database for knowledge relationships.

**Decision**: Use NetworkX (in-memory) for graph storage.

**Rationale**:
- No external dependencies
- Rich graph algorithms
- Easy serialization
- Sufficient for knowledge graph scale

**Consequences**:
- In-memory only (needs persistence strategy)
- Not distributed

---

## ADR-006: Tauri for Frontend

**Status**: Accepted

**Context**: Need a desktop app framework that is lightweight, secure, and performant.

**Decision**: Use Tauri with React and TypeScript.

**Rationale**:
- Lightweight (smaller than Electron)
- Secure by default
- Native performance
- React ecosystem
- TypeScript support

**Consequences**:
- Rust learning curve for native features
- Smaller community than Electron

---

## ADR-007: Ollama as Primary Provider

**Status**: Accepted

**Context**: Need a local AI model provider that requires no API keys.

**Decision**: Use Ollama as the primary model provider.

**Rationale**:
- Fully local (no internet required)
- No API keys
- Open source
- Easy model management
- Good performance

**Consequences**:
- Requires local GPU for best performance
- Model quality varies

---

## ADR-008: Plugin Architecture

**Status**: Accepted

**Context**: Need extensibility without modifying core engine.

**Decision**: Implement plugin system with process isolation.

**Rationale**:
- Extensibility without core changes
- Community ecosystem potential
- Security through isolation
- Replaceable components

**Consequences**:
- Plugin API design complexity
- Sandboxing overhead

---

## ADR-009: Indexing System for Token Saving

**Status**: Accepted

**Context**: Need to reduce AI token usage by loading only relevant context.

**Decision**: Build an indexing system that stores embeddings and provides retrieval.

**Rationale**:
- Dramatically reduces token usage
- Faster AI responses
- Scalable context management
- Enables large codebase support

**Consequences**:
- Additional infrastructure
- Index maintenance overhead

---

## ADR-010: Apache-2.0 License

**Status**: Pending

**Context**: Need to choose an open source license.

**Decision**: TBD (Apache-2.0 recommended for permissiveness).

**Rationale**: TBD

**Consequences**: TBD

---

## ADR-011: Disable OpenSearch Security Plugin

**Status**: Accepted

**Context**: OpenSearch 2.11.0 with security plugin enabled causes SSL errors (`NotSslRecordException: not an SSL/TLS record`) when services try to connect via plain HTTP.

**Decision**: Disable the OpenSearch security plugin by setting `DISABLE_SECURITY_PLUGIN=true` in the environment.

**Rationale**:
- The security plugin expects HTTPS connections, but internal services use plain HTTP
- Disabling security simplifies local development and internal service communication
- For production, a reverse proxy with TLS termination should be used instead

**Consequences**:
- OpenSearch runs without authentication/encryption (acceptable for local development)
- Production deployments should add TLS via reverse proxy

---

## ADR-012: Loki 2.9.x Configuration Format

**Status**: Accepted

**Context**: Loki 2.9.0 failed to start with error: `yaml: unmarshal errors: line 11: field directory not found in type common.FilesystemConfig`

**Decision**: Use `storage_config.filesystem.directory` instead of `common.storage.filesystem.directory` in the Loki configuration.

**Rationale**:
- Loki 2.9.x changed the configuration schema
- The `directory` field moved from `common.storage` to `storage_config.filesystem`
- Referenceana.com/docs/loki/latest/configure/

**Consequences**:
- Loki config is now compatible with 2.9.x
- Future upgrades should check for schema changes

---

---

## ADR-013: Backend Lifecycle Handler Fix

**Status**: Accepted

**Context**: Backend failed to start with error: `TypeError: 'coroutine' object is not callable` in `main.py` lifespan handler.

**Decision**: Changed `start_handler = create_start_app_handler(app)` to `start_handler = await create_start_app_handler(app)` since the function is async.

**Rationale**:
- `create_start_app_handler` is an async function that returns a handler
- The original code tried to call the coroutine as a function
- Adding `await` properly gets the handler function

**Consequences**:
- Backend now starts correctly
- All initialization (database, vector store, graph store) runs properly

---
