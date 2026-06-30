# AIOS - System Design Document

## 1. Introduction

### 1.1 Purpose

This System Design Document describes the architecture, components, interfaces, and data flows of AIOS (Artificial Intelligence Operating System). It provides the architectural blueprint for implementation.

### 1.2 Scope

This design covers:
- System architecture and component decomposition
- Data architecture and storage strategies
- API design and communication patterns
- Security architecture
- Integration points with external systems
- Deployment architecture (local-first desktop)

### 1.3 Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary Language | Python 3.11+ | AI/ML ecosystem, async support, rapid development |
| Frontend Framework | Tauri (Rust) | Lightweight, secure, native performance, small bundle |
| API Framework | FastAPI | Async, auto-docs, Pydantic validation, Python ecosystem |
| Primary Database | SQLite | Embedded, zero-config, local-first, sufficient for target scale |
| Vector Store | Qdrant | Open source, embedded mode, semantic search |
| Graph Store | NetworkX / Neo4j | Relationship tracking for knowledge and memory |
| Message Queue | Redis Streams (optional) / asyncio | Lightweight async task queue |
| Container Runtime | Docker (optional) | Sandboxed tool execution |

---

## 2. System Architecture

### 2.1 High-Level Architecture

AIOS follows a **layered microservices-inspired architecture** within a single desktop application:

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri Frontend                       │
│  (React/TypeScript - Dashboard, Config, Monitoring)     │
├─────────────────────────────────────────────────────────┤
│                   API Gateway Layer                      │
│         (FastAPI - Auth, Routing, Rate Limiting)        │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│  Agent   │ Workflow │ Memory   │Knowledge │  Plugin    │
│  Engine  │ Engine   │ Service  │  Base    │  Manager   │
├──────────┴──────────┴──────────┴──────────┴────────────┤
│                 Core Services Layer                      │
│  (Provider Router, Security, Observability, Config)     │
├─────────────────────────────────────────────────────────┤
│                  Data Access Layer                       │
│       (SQLite, Qdrant, NetworkX, File System)           │
├─────────────────────────────────────────────────────────┤
│               Infrastructure Layer                       │
│    (Process Manager, Network Stack, System APIs)        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Component Architecture

#### 2.2.1 Tauri Frontend

The frontend is built with React/TypeScript within the Tauri framework:

- **Dashboard**: System health, active agents, recent activity
- **Project Manager**: Project creation, configuration, Git integration
- **Agent Monitor**: Real-time agent status, logs, performance
- **Workflow Designer**: Visual workflow creation and editing
- **Memory Explorer**: Browse and search across memory types
- **Knowledge Browser**: Search and navigate knowledge base
- **Configuration**: Provider setup, plugin management, preferences
- **Security Center**: Audit logs, secret management, access control

#### 2.2.2 API Gateway

The API Gateway handles all frontend-to-backend communication:

- **Authentication**: JWT-based session management
- **Request Routing**: Route to appropriate backend service
- **Rate Limiting**: Prevent resource exhaustion
- **Request Validation**: Pydantic schema validation
- **WebSocket Management**: Real-time event streaming
- **CORS/Security Headers**: Security hardening

#### 2.2.3 Agent Engine

The Agent Engine manages all AI agents:

```
AgentEngine
├── AgentRegistry (role definitions, capabilities)
├── AgentFactory (agent instantiation)
├── AgentExecutor (task execution)
├── AgentCommunicator (inter-agent messaging)
└── AgentMonitor (health, performance, lifecycle)
```

Each agent follows this structure:
```python
class BaseAgent:
    role: AgentRole
    model_provider: Provider
    capabilities: List[Capability]
    memory_access: MemoryService
    knowledge_access: KnowledgeBase
    tools: List[Tool]
    config: AgentConfig
```

#### 2.2.4 Workflow Engine

The Workflow Engine orchestrates task execution:

```
WorkflowEngine
├── DAGParser (workflow definition parsing)
├── DependencyResolver (task ordering)
├── TaskScheduler (execution scheduling)
├── ParallelExecutor (concurrent task execution)
├── ApprovalGate (human-in-the-loop)
└── WorkflowStore (persistence)
```

#### 2.2.5 Memory Service

The Memory Service manages all memory types:

```
MemoryService
├── ShortTermStore (session context, Redis/in-memory)
├── LongTermStore (persistent, SQLite)
├── VectorStore (semantic search, Qdrant)
├── GraphStore (relationships, NetworkX)
├── DecisionStore (choices + rationale, SQLite)
├── ProjectStore (project context, SQLite)
├── ConversationStore (chat history, SQLite)
├── ArchitectureStore (design decisions, SQLite)
└── LearningStore (patterns, SQLite)
```

#### 2.2.6 Knowledge Base

The Knowledge Base handles document indexing and retrieval:

```
KnowledgeBase
├── Indexer (document parsing, chunking)
├── Embedder (text embedding generation)
├── SearchEngine (semantic search)
├── GraphBuilder (knowledge graph construction)
├── FreshnessMonitor (staleness detection)
└── ImportManager (source connectors)
```

#### 2.2.7 Plugin Manager

The Plugin Manager handles extensibility:

```
PluginManager
├── PluginLoader (discovery and loading)
├── PluginSandbox (isolation layer)
├── PluginRegistry (metadata and capabilities)
├── PluginAPI (SDK interface)
└── PluginValidator (security validation)
```

#### 2.2.8 Provider Router

The Provider Router manages AI model providers:

```
ProviderRouter
├── ProviderRegistry (available providers)
├── CapabilityMapper (model capabilities)
├── TaskRouter (intelligent dispatching)
├── FallbackChain (failure handling)
├── UsageTracker (token/cost tracking)
└── ModelPool (model instances)
```

---

## 3. Data Architecture

### 3.1 Storage Strategy

| Data Type | Storage Engine | Justification |
|-----------|---------------|---------------|
| Structured data | SQLite | Embedded, ACID, zero-config |
| Vector embeddings | Qdrant | Semantic search, filtering |
| Graph relationships | NetworkX (in-memory) / Neo4j (optional) | Relationship queries |
| Session cache | Python dicts + Redis (optional) | Fast access, TTL support |
| File artifacts | File system | Large blobs, Git repos |
| Logs | Structured files + SQLite | Queryable, rotatable |

### 3.2 Database Schema (Core Tables)

```sql
-- Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    path TEXT NOT NULL,
    config JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Agents
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    role TEXT NOT NULL,
    name TEXT,
    config JSON,
    model_provider TEXT,
    model_name TEXT,
    status TEXT,
    created_at TIMESTAMP
);

-- Workflows
CREATE TABLE workflows (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    name TEXT NOT NULL,
    definition JSON NOT NULL,
    status TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Tasks
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    workflow_id TEXT REFERENCES workflows(id),
    agent_id TEXT REFERENCES agents(id),
    type TEXT NOT NULL,
    status TEXT,
    input JSON,
    output JSON,
    dependencies TEXT[], -- array of task IDs
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error TEXT
);

-- Memory entries
CREATE TABLE memory_entries (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    memory_type TEXT NOT NULL, -- short_term, long_term, vector, graph, decision, project, conversation, architecture, learning
    key TEXT NOT NULL,
    value JSON,
    metadata JSON,
    embedding_id TEXT, -- reference to Qdrant
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    expires_at TIMESTAMP
);

-- Knowledge entries
CREATE TABLE knowledge_entries (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    source_type TEXT NOT NULL, -- docs, git, research, api, wiki
    source_uri TEXT,
    title TEXT,
    content TEXT,
    metadata JSON,
    embedding_id TEXT,
    indexed_at TIMESTAMP,
    freshness_score REAL
);

-- Audit logs
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMP,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    details JSON,
    ip_address TEXT
);

-- Plugins
CREATE TABLE plugins (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    author TEXT,
    description TEXT,
    plugin_type TEXT, -- agent, tool, provider, workflow, memory
    manifest JSON,
    installed_at TIMESTAMP,
    enabled BOOLEAN
);

-- Secrets (encrypted)
CREATE TABLE secrets (
    id TEXT PRIMARY KEY,
    project_id TEXT REFERENCES projects(id),
    key_hash TEXT NOT NULL, -- SHA-256 of key name
    encrypted_value BLOB NOT NULL, -- AES-256 encrypted
    nonce BLOB NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### 3.3 Vector Store Schema (Qdrant)

```python
# Memory vectors collection
memory_collection = {
    "name": "memory_vectors",
    "vectors": {
        "size": 1536,  # Embedding dimension (model-dependent)
        "distance": "Cosine"
    },
    "payload_schema": {
        "project_id": "keyword",
        "memory_type": "keyword",
        "agent_id": "keyword",
        "timestamp": "datetime",
        "tags": "keyword[]"
    }
}

# Knowledge vectors collection
knowledge_collection = {
    "name": "knowledge_vectors",
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "project_id": "keyword",
        "source_type": "keyword",
        "source_uri": "text",
        "title": "text",
        "indexed_at": "datetime"
    }
}
```

---

## 4. API Design

### 4.1 REST API Endpoints

#### Projects
```
POST   /api/v1/projects                    # Create project
GET    /api/v1/projects                    # List projects
GET    /api/v1/projects/{id}               # Get project
PUT    /api/v1/projects/{id}               # Update project
DELETE /api/v1/projects/{id}               # Delete project
POST   /api/v1/projects/{id}/clone         # Clone project
```

#### Agents
```
POST   /api/v1/agents                      # Create agent
GET    /api/v1/agents                      # List agents
GET    /api/v1/agents/{id}                 # Get agent
PUT    /api/v1/agents/{id}                 # Update agent
DELETE /api/v1/agents/{id}                 # Delete agent
POST   /api/v1/agents/{id}/execute         # Execute task
POST   /api/v1/agents/{id}/pause           # Pause agent
POST   /api/v1/agents/{id}/resume          # Resume agent
GET    /api/v1/agents/{id}/logs            # Get agent logs
```

#### Workflows
```
POST   /api/v1/workflows                   # Create workflow
GET    /api/v1/workflows                   # List workflows
GET    /api/v1/workflows/{id}              # Get workflow
PUT    /api/v1/workflows/{id}              # Update workflow
DELETE /api/v1/workflows/{id}              # Delete workflow
POST   /api/v1/workflows/{id}/execute      # Start workflow
POST   /api/v1/workflows/{id}/pause        # Pause workflow
POST   /api/v1/workflows/{id}/approve      # Approve gate
GET    /api/v1/workflows/{id}/status       # Get status
```

#### Memory
```
POST   /api/v1/memory                      # Store memory
GET    /api/v1/memory                      # Query memory
GET    /api/v1/memory/{id}                 # Get memory entry
DELETE /api/v1/memory/{id}                 # Delete memory
POST   /api/v1/memory/search               # Semantic search
GET    /api/v1/memory/types                # List memory types
```

#### Knowledge
```
POST   /api/v1/knowledge/index             # Index document
GET    /api/v1/knowledge/search            # Search knowledge
GET    /api/v1/knowledge/{id}              # Get entry
DELETE /api/v1/knowledge/{id}              # Delete entry
GET    /api/v1/knowledge/graph             # Get knowledge graph
```

#### Plugins
```
POST   /api/v1/plugins                     # Install plugin
GET    /api/v1/plugins                     # List plugins
GET    /api/v1/plugins/{id}                # Get plugin
DELETE /api/v1/plugins/{id}                # Uninstall plugin
POST   /api/v1/plugins/{id}/enable         # Enable plugin
POST   /api/v1/plugins/{id}/disable        # Disable plugin
```

#### Providers
```
GET    /api/v1/providers                   # List providers
POST   /api/v1/providers                   # Add provider
PUT    /api/v1/providers/{id}              # Update provider
DELETE /api/v1/providers/{id}              # Remove provider
GET    /api/v1/providers/{id}/models       # List available models
POST   /api/v1/providers/{id}/test         # Test connection
```

#### System
```
GET    /api/v1/system/health               # Health check
GET    /api/v1/system/metrics              # System metrics
GET    /api/v1/system/logs                 # System logs
GET    /api/v1/system/config               # Get configuration
PUT    /api/v1/system/config               # Update configuration
```

### 4.2 WebSocket Events

```javascript
// Agent events
agent.created
agent.started
agent.completed
agent.failed
agent.log

// Workflow events
workflow.started
workflow.task.started
workflow.task.completed
workflow.task.failed
workflow.approval.required
workflow.completed

// System events
system.health.update
system.metrics.update
system.notification

// Memory events
memory.created
memory.updated
memory.deleted
```

### 4.3 Internal Communication

Components communicate through an **event bus** pattern:

```python
class EventBus:
    async def publish(self, event: Event) -> None
    async def subscribe(self, event_type: str, handler: Callable) -> None
    async def unsubscribe(self, event_type: str, handler: Callable) -> None
```

---

## 5. Security Architecture

### 5.1 Authentication & Authorization

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User/IDE   │────▶│  API Gateway │────▶│  Auth Layer  │
└──────────────┘     └──────────────┘     └──────────────┘
                                                   │
                                          ┌──────────────┐
                                          │   RBAC Engine │
                                          └──────────────┘
                                                   │
                                          ┌──────────────┐
                                          │  Policy Store │
                                          └──────────────┘
```

**Roles**: Admin, Project Owner, Developer, Viewer, Agent

**Permissions**: Granular permissions per resource type (project, agent, workflow, memory, knowledge, plugin, system)

### 5.2 Secret Management

- AES-256-GCM encryption for all secrets at rest
- Master key derived from user password (PBKDF2)
- Memory-only decryption during use
- Automatic secret rotation reminders
- No secrets in logs or error messages

### 5.3 Plugin Security

- Plugin signature verification (Ed25519)
- Process-level sandboxing (seccomp/AppArmor)
- Resource limits (CPU, memory, network)
- Read-only filesystem access by default
- Explicit permission grants per plugin

### 5.4 Audit Trail

All actions are logged with:
- Timestamp
- Actor (user or agent)
- Action type
- Resource affected
- Input/output summary
- Success/failure status

---

## 6. Provider Architecture

### 6.1 Provider Abstraction

```python
class BaseProvider(ABC):
    """Abstract base for all AI model providers"""

    @abstractmethod
    async def chat_completion(self, messages: List[Message], **kwargs) -> Response:
        ...

    @abstractmethod
    async def stream_completion(self, messages: List[Message], **kwargs) -> AsyncIterator[Response]:
        ...

    @abstractmethod
    async def list_models(self) -> List[Model]:
        ...

    @abstractmethod
    async def get_capabilities(self, model: str) -> ModelCapabilities:
        ...

    @abstractmethod
    async def count_tokens(self, text: str, model: str) -> int:
        ...
```

### 6.2 Supported Providers

| Provider | Type | Models | Auth |
|----------|------|--------|------|
| Ollama | Local | All local models | None |
| OpenRouter | API (free tier) | Free models only | API Key |
| LiteLLM | Proxy | Configurable | API Key |
| LM Studio | Local | All local models | None |
| vLLM | Local | All supported | None |
| HuggingFace | API (free tier) | Free models | Token |

### 6.3 Model Routing Strategy

1. **Capability Matching**: Route tasks to models that declare required capabilities
2. **Availability Check**: Verify provider is online before routing
3. **Load Balancing**: Distribute across available instances
4. **Cost Optimization**: Prefer free models, track usage
5. **Fallback Chain**: Automatic failover on provider failure

---

## 7. Deployment Architecture

### 7.1 Local-First Desktop

```
┌─────────────────────────────────────────────────────────┐
│                    AIOS Desktop App                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Tauri Runtime (Rust)                │    │
│  │  ┌───────────────────────────────────────────┐  │    │
│  │  │         Frontend (React/TS)               │  │    │
│  │  └───────────────────────────────────────────┘  │    │
│  │  ┌───────────────────────────────────────────┐  │    │
│  │  │      Backend (Python/FastAPI)             │  │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌────────────┐  │  │    │
│  │  │  │  API    │ │  Agent  │ │  Workflow  │  │  │    │
│  │  │  │ Gateway │ │ Engine  │ │  Engine    │  │  │    │
│  │  │  └─────────┘ └─────────┘ └────────────┘  │  │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌────────────┐  │  │    │
│  │  │  │ Memory  │ │Knowledge│ │  Provider  │  │  │    │
│  │  │  │ Service │ │  Base   │ │  Router    │  │  │    │
│  │  │  └─────────┘ └─────────┘ └────────────┘  │  │    │
│  │  └───────────────────────────────────────────┘  │    │
│  │  ┌───────────────────────────────────────────┐  │    │
│  │  │         Embedded Storage                  │  │    │
│  │  │  ┌─────────┐ ┌─────────┐ ┌────────────┐  │  │    │
│  │  │  │ SQLite  │ │ Qdrant  │ │  NetworkX  │  │  │    │
│  │  │  └─────────┘ └─────────┘ └────────────┘  │  │    │
│  │  └───────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 7.2 Optional Cloud Sync

- Git-based project sync (GitHub, Gitea, Forgejo)
- Encrypted backup to cloud storage
- Optional remote monitoring dashboard
- Plugin registry for sharing

### 7.3 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Disk | 50 GB | 100 GB+ |
| RAM | 16 GB | 32 GB |
| CPU | 4 cores | 8+ cores |
| GPU | None | NVIDIA 8GB+ VRAM |

---

## 8. Error Handling Strategy

### 8.1 Error Categories

| Category | Handling | Recovery |
|----------|----------|----------|
| Provider timeout | Retry with exponential backoff | Auto-fallback to next provider |
| Provider rate limit | Queue and retry | Auto with delay |
| Agent error | Log and notify | Manual retry or reassign |
| Workflow failure | Pause workflow | Human decision |
| Memory corruption | Rebuild from logs | Auto-recovery |
| Plugin crash | Isolate and disable | Auto-disable plugin |

### 8.2 Circuit Breaker Pattern

```python
class CircuitBreaker:
    """Prevents cascading failures"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Failing, reject requests
    HALF_OPEN = "HALF_OPEN" # Testing recovery

    async def call(self, func, *args, **kwargs):
        if self.state == self.OPEN:
            if self.should_attempt_reset():
                self.state = self.HALF_OPEN
            else:
                raise CircuitOpenError(...)
        # ... execute with failure tracking
```

---

## 9. Observability Architecture

### 9.1 Three Pillars

1. **Logs**: Structured JSON logs, rotatable, queryable
2. **Metrics**: Prometheus-compatible metrics endpoint
3. **Traces**: OpenTelemetry spans for request flows

### 9.2 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| agent_tasks_total | Counter | Total agent tasks executed |
| agent_task_duration | Histogram | Task execution time |
| provider_requests_total | Counter | API calls per provider |
| provider_latency | Histogram | API response time |
| memory_operations_total | Counter | Memory CRUD operations |
| knowledge_index_size | GB | Documents indexed |
| workflow_completion_rate | Gauge | Success rate |
| token_usage_total | Counter | Tokens consumed per model |

---

## 10. Appendix: Technology Stack Summary

| Layer | Technology | Version | License |
|-------|-----------|---------|---------|
| Frontend | React | 18+ | MIT |
| Frontend | TypeScript | 5+ | Apache-2.0 |
| Desktop Shell | Tauri | 2+ | MIT/Apache-2.0 |
| Backend | Python | 3.11+ | PSF |
| API Framework | FastAPI | 0.110+ | MIT |
| Validation | Pydantic | 2+ | MIT |
| Database | SQLite | 3.45+ | Public Domain |
| Vector DB | Qdrant | 1.8+ | Apache-2.0 |
| Graph | NetworkX | 3+ | BSD-3 |
| Async | asyncio | stdlib | PSF |
| Task Queue | Celery (optional) | 5+ | BSD-3 |
| Testing | Pytest | 8+ | MIT |
| Linting | Ruff | latest | MIT |
| Packaging | PyInstaller | latest | MIT |
| Docs | MkDocs | latest | BSD-3 |
