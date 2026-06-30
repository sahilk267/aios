# AIOS v1.0.0-stable - Quick Reference

## 5 Essential Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View container logs
docker-compose logs -f [service-name]

# Restart a specific service
docker-compose restart [service-name]

# List all running containers
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 3 Essential curl Commands

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# List all agents
curl http://localhost:8000/api/v1/agents

# Execute a workflow (example)
curl -X POST http://localhost:8000/api/v1/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "test task"}'
```

## Token Savings Query

```python
# Query the indexing system for token savings
from aios.knowledge.indexer import Indexer
from aios.memory.vector import VectorStore

# Initialize
indexer = Indexer()
vector_store = VectorStore()

# Query with context
query = "What are the core responsibilities of the Meta-Controller Agent?"
results = vector_store.search(query, limit=5)

# Calculate savings
full_tokens = len(query.encode()) * 4  # Approximate
retrieved_tokens = sum(len(chunk.encode()) * 4 for chunk in results)
savings = (1 - retrieved_tokens / full_tokens) * 100

print(f"Full tokens: {full_tokens}")
print(f"Retrieved tokens: {retrieved_tokens}")
print(f"Token savings: {savings:.1f}%")
```

## Service Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Grafana | http://localhost:3000 | admin/aios12345 |
| Prometheus | http://localhost:9090 | - |
| OpenSearch | http://localhost:9200 | - |
| Loki | http://localhost:3100 | - |
| n8n | http://localhost:5678 | - |
| Gitea | http://localhost:3001 | - |

## Common Issues

See `HANDOVER.md` for detailed troubleshooting including:
- Loki configuration fixes
- OpenSearch SSL fixes
- Neo4j plugin fixes
- Backend import fixes
- Ollama port conflicts
