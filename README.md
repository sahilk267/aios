# AIOS - Artificial Intelligence Operating System

[![CI](https://github.com/aios-project/aios/actions/workflows/ci.yml/badge.svg)](https://github.com/aios-project/aios/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)

AIOS is the world's first **Open Source Self-Evolving AI Engineering Platform**. It is designed to build itself continuously through safe iterations.

## � Mission

Build a platform capable of building itself continuously through safe iterations.

## ✨ Features

- **� Multi-Agent System** - 13 specialized AI agents for different engineering roles
- **� Memory & Knowledge** - 9 memory types with vector and graph storage
- **🔄 Self-Evolution** - Safe self-improvement with human approval gates
- **� Plugin System** - Extensible architecture with process isolation
- **📊 Observability** - Prometheus metrics, Grafana dashboards, distributed tracing
- **🔒 Security** - RBAC, audit logging, secret management
- **🏠 Local-First** - Runs entirely locally, no paid APIs required

## �️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Tauri)                       │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
�─────────────────────────────────────────────────────────────┐
│                      API Gateway (FastAPI)                    │
└─────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────�
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────�
│  Agent Engine │      │ Memory System │      │  Knowledge   │
│  (13 Agents)  │      │  (9 Types)   │      │    Base      │
└──────────────�      └──────────────�      └──────────────�
        │                       │                       │
        └───────────────────────�───────────────────────┘
                                ▼
�─────────────────────────────────────────────────────────────┐
│              Data Layer (SQLite, Qdrant, NetworkX)            │
└─────────────────────────────────────────────────────────────┘
```

## � Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/aios-project/aios.git
cd aios

# Run setup script
./scripts/setup.sh

# Start all services
docker-compose up -d

# Start development server
./scripts/dev.sh
```

### Access Points

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |
| n8n | http://localhost:5678 |
| Gitea | http://localhost:3001 |

## � Documentation

- [Software Requirements](SRS.md)
- [System Design](SystemDesign.md)
- [Repository Structure](RepositoryStructure.md)
- [Implementation Roadmap](ImplementationRoadmap.md)
- [Dependency Graph](DependencyGraph.md)
- [Coding Standards](CodingStandards.md)
- [AI Governance Rules](AIGovernanceRules.md)
- [Indexing Strategy](INDEXING_STRATEGY.md)

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Run specific test categories
cd backend
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v
```

## �️ Development

### Project Structure

```
aios/
├── backend/          # Python FastAPI backend
├── frontend/         # Tauri + React frontend
├── plugins/          # Plugin ecosystem
├── scripts/          # Development scripts
├── config/           # Configuration files
├── data/             # Runtime data (gitignored)
└── docs/             # Documentation
```

### Core Principles

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

## 🤝 Contributing

See [Contribution Guide](ContributionGuide.md) for details on how to contribute.

## 📄 License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.

## � Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Ollama](https://ollama.ai/) - Local AI models
- [Qdrant](https://qdrant.tech/) - Vector database
- [Tauri](https://tauri.app/) - Desktop app framework
