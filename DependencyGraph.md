# AIOS - Dependency Graph

## 1. Overview

This document maps the dependencies between AIOS components, services, and external systems. Understanding these dependencies is critical for development ordering, testing strategy, and deployment.

## 2. Component Dependency Graph

```
                                    ┌──────────────┐
                                    │   Frontend   │
                                    │   (Tauri)    │
                                    └──────┬───────┘
                                           │ HTTP/WebSocket
                                           ▼
                                    ┌──────────────┐
                                    │ API Gateway  │
                                    └──────┬───────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
             ┌────────────┐         ┌────────────┐         ┌────────────┐
             │  Security  │         │   Config   │         │   Events   │
             │  Service   │         │   Service  │         │   (Bus)    │
             └─────┬──────┘         └─────┬──────┘         └─────┬──────┘
                   │                      │                      │
                   │            ┌─────────┴─────────┐            │
                   │            │                   │            │
                   ▼            ▼                   ▼            ▼
            ┌──────────┐ ┌──────────┐       ┌──────────┐ ┌──────────┐
            │  Audit   │ │ Database │       │  Logger  │ │  Health  │
            │  Log     │ │  (SQLite)│       │          │ │  Check   │
            └──────────┘ └────┬─────┘       └──────────┘ └──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
 ┌────────────┐        ┌────────────┐        ┌────────────┐
 │   Memory   │        │  Knowledge │        │   Plugin   │
 │  Service   │        │   Base     │        │  Manager   │
 └─────┬──────┘        └─────┬──────┘        └─────┬──────┘
       │                     │                     │
       ├──────────┬──────────┤                     │
       │          │          │                     │
       ▼          ▼          ▼                     ▼
 ┌──────────┐┌──────────┐┌──────────┐       ┌──────────┐
 │ Qdrant   ││ NetworkX ││  SQLite  │       │ Sandbox  │
 │ (Vector) ││ (Graph)  ││ (Memory) │       │ (Process)│
 └──────────┘└──────────┘└──────────┘└──────────┘
        │
        ▼
 ┌────────────────────────────────────────────────────────────┐
 │                    Engine Layer                              │
 │  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
 │  │   Agent    │  │  Workflow  │  │  Provider  │           │
 │  │   Engine   │  │   Engine   │  │   Router   │           │
 │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
 │        │               │               │                   │
 │        └───────────────┼───────────────┘                   │
 │                        │                                   │
 │                        ▼                                   │
 │              ┌──────────────────┐                          │
 │              │   Task Scheduler │                          │
 │              └──────────────────┘                          │
 └────────────────────────────────────────────────────────────┘
        │
        ▼
 ┌────────────────────────────────────────────────────────────┐
 │                   Provider Layer                            │
 │  ┌─────────┐ ┌───────────┐ ┌────────┐ ┌─────────┐        │
 │  │ Ollama  │ │ OpenRouter│ │ LiteLLM│ │   vLLM  │        │
 │  └─────────┘ └───────────┘ └────────┘ └─────────┘        │
 │  ┌─────────┐ ┌───────────┐ ┌────────┐                    │
 │  │LM Studio│ │ OpenAI-   │ │Hugging │                    │
 │  │         │ │ Compat    │ │ Face   │                    │
 │  └─────────┘ └───────────┘ └────────┘                    │
 └────────────────────────────────────────────────────────────┘
```

## 3. Service Dependencies

### 3.1 Core Services

| Service | Depends On | Required By |
|---------|-----------|-------------|
| Config Service | File System | All services |
| Event Bus | Config Service | All services |
| Logger | Config Service | All services |
| Health Check | All services | API Gateway |
| Database (SQLite) | File System | All persistent services |

### 3.2 Engine Services

| Service | Depends On | Required By |
|---------|-----------|-------------|
| Agent Engine | Provider Router, Memory Service, Event Bus | Workflow Engine, API |
| Workflow Engine | Agent Engine, Task Scheduler, Event Bus | API |
| Task Scheduler | Agent Engine, Event Bus | Workflow Engine |
| Provider Router | Config Service, Provider Plugins | Agent Engine |

### 3.3 Data Services

| Service | Depends On | Required By |
|---------|-----------|-------------|
| Memory Service | SQLite, Qdrant, NetworkX, Event Bus | Agent Engine, Knowledge Base |
| Knowledge Base | Qdrant, SQLite, Event Bus | Agent Engine, Memory Service |
| Plugin Manager | Config Service, Sandbox, Event Bus | API |
| Security Service | SQLite, Config Service | API Gateway |

## 4. External Dependencies

### 4.1 AI Model Providers

| Provider | Type | Auth Required | Rate Limits |
|----------|------|---------------|-------------|
| Ollama | Local | None | None |
| OpenRouter | API | API Key | Yes (free tier) |
| LiteLLM | Proxy | Configurable | Configurable |
| LM Studio | Local | None | None |
| vLLM | Local | None | None |
| HuggingFace | API | Token (free) | Yes |

### 4.2 Tool Integrations

| Tool | Integration Type | Required For |
|------|-----------------|--------------|
| Git | CLI/libgit2 | Version control, knowledge indexing |
| Docker | API (optional) | Containerized tool execution |
| MCP Servers | MCP Protocol | Extended tool capabilities |
| VS Code | Extension API | IDE integration |
| Cursor | Extension API | IDE integration |

### 4.3 Data Stores

| Store | Type | Embedded | Used For |
|-------|------|----------|----------|
| SQLite | Relational | Yes | Structured data, metadata |
| Qdrant | Vector | Yes | Semantic search, embeddings |
| NetworkX | Graph | Yes (in-memory) | Knowledge graph, relationships |
| File System | Files | Yes | Logs, configs, artifacts |

## 5. Build Dependencies

### 5.1 Frontend Build Chain

```
TypeScript Source
    │
    ▼
TypeScript Compiler (tsc)
    │
    ▼
Vite Bundler
    │
    ├──▶ React Runtime
    │
    └──▶ Tauri Runtime (Rust)
            │
            ▼
        Platform Binary
```

### 5.2 Backend Build Chain

```
Python Source
    │
    ▼
Ruff (Lint + Format)
    │
    ▼
Pytest (Test)
    │
    ▼
PyInstaller (Package)
    │
    ▼
Executable Bundle
```

## 6. Runtime Dependencies

### 6.1 Startup Order

```
1. Configuration Service
2. Logger
3. Event Bus
4. Database (SQLite)
5. Vector Store (Qdrant)
6. Graph Store (NetworkX)
7. Health Check
8. Provider Router
9. Memory Service
10. Knowledge Base
11. Plugin Manager
12. Security Service
13. Agent Engine
14. Workflow Engine
15. API Gateway
16. WebSocket Server
17. Frontend (Tauri)
```

### 6.2 Shutdown Order

Reverse of startup, with graceful connection draining.

## 7. Test Dependencies

### 7.1 Test Pyramid

```
            ╱╲
           ╱  ╲
          ╱ E2E╲          Few: Full system tests
         ╱──────╲
        ╱        ╲
       ╱ Integration╲     Some: Service boundaries
      ╱──────────────╲
     ╱                ╲
    ╱    Unit Tests     ╲  Many: Individual functions
   ╱────────────────────╲
```

### 7.2 Test Dependencies

| Test Type | Depends On | Mocks |
|-----------|-----------|-------|
| Unit | Nothing | All external |
| Integration | SQLite, Qdrant | Providers |
| E2E | All services | None (or sandbox providers) |

## 8. Critical Path

The critical path for initial development:

```
Config → Logger → Event Bus → Database → Provider Router → Agent Engine → API Gateway → Frontend
```

Any delay on the critical path delays the entire project.

## 9. Dependency Risk Matrix

| Dependency | Risk Level | Mitigation |
|-----------|-----------|-----------|
| Ollama API changes | Low | Version pin, abstraction layer |
| Qdrant API changes | Medium | Version pin, migration scripts |
| SQLite corruption | Low | Backups, WAL mode |
| Tauri breaking changes | Medium | Pin version, track changelog |
| FastAPI breaking changes | Low | Pin version, stable API |
| Model availability | High | Multiple providers, fallback chains |
| Plugin malicious code | High | Sandboxing, validation, signing |
