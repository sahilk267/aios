# AIOS Indexing Strategy

## Overview

The AIOS Indexing System is designed to drastically reduce token usage by storing embeddings of all code modules, documentation, decisions, and state files into a vector database (Qdrant). Instead of loading full documents into the token window, the AI uses a retrieval function to fetch only the most relevant context chunks.

## Architecture

```
┌─────────────────────────────────────────────────────────────�
│                     Indexing Pipeline                        │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐│
│  │  File     │───▶│  Chunk   │───▶│ Embed   │───▶│ Store  ││
│  │  Watcher  │    │  Text    │    │ Vector  │    │ Qdrant ││
│  └──────────┘    └──────────�    └──────────┘    └────────┘│
│       │                                            │        │
│       │         ┌──────────┐                       │        │
│       └────────▶│  Change  │───────────────────────┘        │
│                 │  Detect  │                                │
│                 └──────────�                                │
└─────────────────────────────────────────────────────────────�

┌─────────────────────────────────────────────────────────────┐
│                     Retrieval Pipeline                       │
│                                                             │
│ ──┐    ┌──────────┐    ┌──────────┐    ┌────────┐│
│  │  Query   │───▶│  Embed   │───▶│ Search  │───▶│ Format ││
│  │  Input   │    │  Query   │    │ Qdrant  │    │ Output ││
│  └──────────�    └──────────┘    └──────────┘    └────────�│
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. File Watcher (`scripts/file_watcher.py`)
- Monitors file system for changes
- Triggers re-indexing on file modification
- Supports Git hook integration

### 2. Indexing Engine (`aios/knowledge/indexer.py`)
- Chunks text into overlapping segments
- Generates embeddings for each chunk
- Stores embeddings in Qdrant
- Tracks file hashes for change detection

### 3. Retrieval API (`search_index`, `get_relevant_context`)
- Accepts natural language queries
- Returns most relevant context chunks
- Respects token limits
- Supports source filtering

## Chunking Strategy

- **Chunk Size**: 1000 characters (configurable)
- **Overlap**: 200 characters (configurable)
- **Rationale**: Balances context preservation with retrieval precision

## Embedding Model

- **Current**: Simple hash-based embedding (placeholder)
- **Production**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Distance Metric**: Cosine similarity

## Supported File Types

| Extension | Type | Priority |
|-----------|------|----------|
| `.py` | Code | High |
| `.md` | Documentation | High |
| `.json` | Data | Medium |
| `.toml` | Config | Medium |
| `.yaml` | Config | Medium |
| `.ts/.tsx` | Code | High |
| `.js/.jsx` | Code | High |
| `.rs` | Code | High |
| `.go` | Code | High |

## Usage

### Indexing a Directory
```python
from aios.knowledge.indexer import index_directory
from pathlib import Path

count = await index_directory(Path("./backend"))
print(f"Indexed {count} files")
```

### Searching the Index
```python
from aios.knowledge.indexer get_relevant_context

# Get raw results
results = await search_index("How does the agent engine work?", limit=5)

# Get formatted context for AI
context = await get_relevant_context(
    "How does the agent engine work?",
    max_tokens=4000
)
```

### Automatic Indexing via File Watcher
```bash
# Start the file watcher
python scripts/file_watcher.py --watch-dir ./backend

# Or use Git hooks
./scripts/install_git_hooks.sh
```

## Token Savings

| Approach | Tokens Used | Savings |
|----------|-------------|---------|
| Full document load | ~10,000+ | - |
| Indexed retrieval | ~2,000-4,000 | 60-80% |

## Configuration

```toml
[indexing]
chunk_size = 1000
chunk_overlap = 200
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
score_threshold = 0.5
max_results = 20
```

## Future Improvements

1. **Better Embeddings**: Use proper sentence-transformers model
2. **Incremental Indexing**: Only re-index changed chunks
3. **Multi-modal**: Support for images, diagrams
4. **Cross-references**: Link related chunks across files
5. **Semantic Caching**: Cache frequent query results
