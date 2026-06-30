"""AIOS Indexing Engine for Token Saving.

This module provides the core indexing system that stores embeddings of all code modules,
documentation, decisions, and state files into a vector database. It provides retrieval
functions that return only the most relevant context chunks, drastically reducing token usage.
"""

import hashlib
import os
import structlog
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from aios.core.config import settings

logger = structlog.get_logger(__name__)

# Supported file extensions for indexing
SUPPORTED_EXTENSIONS = {
    ".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt", ".rst",
    ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go",
    ".java", ".c", ".cpp", ".h", ".hpp", ".sh", ".bash", ".zsh",
    ".sql", ".env.example", ".dockerignore", ".gitignore",
}

# Directories to ignore
IGNORE_DIRS = {
    "__pycache__", "node_modules", ".git", ".venv", "venv",
    "dist", "build", ".eggs", "*.egg-info", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "htmlcov", ".coverage",
    "data/qdrant", "data/sqlite", "data/logs",
}


def should_index_file(file_path: Path) -> bool:
    """Determine if a file should be indexed."""
    # Check if any parent directory is in ignore list
    for parent in file_path.parts:
        if parent in IGNORE_DIRS:
            return False
    
    # Check extension
    return file_path.suffix in SUPPORTED_EXTENSIONS


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Split text into overlapping chunks."""
    chunk_size = chunk_size or settings.index_chunk_size
    overlap = overlap or settings.index_chunk_overlap
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    
    return chunks


def generate_embedding(text: str) -> List[float]:
    """Generate an embedding vector for text.
    
    Uses a simple hash-based embedding for now.
    In production, this would use a proper embedding model.
    """
    # Simple deterministic embedding based on character frequencies
    # This is a placeholder - real implementation would use sentence-transformers
    vector = [0.0] * 384
    
    for i, char in enumerate(text):
        idx = (ord(char) + i) % 384
        vector[idx] += 1.0
    
    # Normalize
    magnitude = sum(x * x for x in vector) ** 0.5
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    
    return vector


def compute_file_hash(file_path: Path) -> str:
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


async def index_file(file_path: Path, force: bool = False) -> Optional[str]:
    """Index a single file into the vector store.
    
    Args:
        file_path: Path to the file to index
        force: Force re-indexing even if unchanged
        
    Returns:
        Document ID if indexed, None if skipped
    """
    if not should_index_file(file_path):
        return None
    
    try:
        from aios.memory.vector import upsert_vector
        
        # Read file content
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        # Compute hash for change detection
        file_hash = compute_file_hash(file_path)
        
        # Generate document ID from relative path
        try:
            rel_path = str(file_path.relative_to(Path.cwd()))
        except ValueError:
            rel_path = str(file_path)
        
        doc_id = hashlib.sha256(rel_path.encode()).hexdigest()[:16]
        
        # Chunk the content
        chunks = chunk_text(content)
        
        # Index each chunk
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            embedding = generate_embedding(chunk)
            
            await upsert_vector(
                id=chunk_id,
                vector=embedding,
                payload={
                    "source": rel_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "hash": file_hash,
                    "content": chunk,
                    "indexed_at": datetime.utcnow().isoformat(),
                    "type": "code" if file_path.suffix in (".py", ".js", ".ts", ".tsx", ".jsx") else "documentation",
                },
            )
        
        logger.info("File indexed", path=rel_path, chunks=len(chunks))
        return doc_id
        
    except Exception as e:
        logger.error("Failed to index file", path=str(file_path), error=str(e))
        return None


async def index_directory(directory: Path, recursive: bool = True) -> int:
    """Index all files in a directory.
    
    Args:
        directory: Directory to index
        recursive: Whether to recurse into subdirectories
        
    Returns:
        Number of files indexed
    """
    count = 0
    
    if recursive:
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                result = await index_file(file_path)
                if result:
                    count += 1
    else:
        for file_path in directory.iterdir():
            if file_path.is_file():
                result = await index_file(file_path)
                if result:
                    count += 1
    
    logger.info("Directory indexed", path=str(directory), files=count)
    return count


async def search_index(
    query: str,
    limit: int = 10,
    source_filter: Optional[str] = None,
    score_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """Search the index for relevant context chunks.
    
    This is the main retrieval function used by the AI to fetch
    only needed information, drastically reducing token usage.
    
    Args:
        query: Search query
        limit: Maximum number of results
        source_filter: Filter by source path pattern
        score_threshold: Minimum similarity score
        
    Returns:
        List of relevant context chunks with metadata
    """
    try:
        from aios.memory.vector import search_vectors
        
        # Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Build filter conditions
        filter_conditions = None
        if source_filter:
            # Note: This is a simplified filter - real implementation
            # would need more sophisticated matching
            pass
        
        # Search vector store
        results = await search_vectors(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions,
        )
        
        # Format results
        context_chunks = []
        for r in results:
            context_chunks.append({
                "content": r["payload"].get("content", ""),
                "source": r["payload"].get("source", ""),
                "score": r["score"],
                "type": r["payload"].get("type", "unknown"),
            })
        
        logger.info("Index search completed", query=query, results=len(context_chunks))
        return context_chunks
        
    except Exception as e:
        logger.error("Index search failed", query=query, error=str(e))
        return []


async def get_relevant_context(
    query: str,
    max_tokens: int = 4000,
    source_filter: Optional[str] = None,
) -> str:
    """Get relevant context for a query, formatted for AI consumption.
    
    This function retrieves the most relevant context chunks and formats
    them for inclusion in AI prompts, respecting token limits.
    
    Args:
        query: The query to find context for
        max_tokens: Maximum tokens to include
        source_filter: Optional source filter
        
    Returns:
        Formatted context string
    """
    chunks = await search_index(query, limit=20, source_filter=source_filter)
    
    if not chunks:
        return ""
    
    # Build context string
    context_parts = []
    current_length = 0
    
    for chunk in chunks:
        # Estimate tokens (rough approximation)
        chunk_tokens = len(chunk["content"].split())
        
        if current_length + chunk_tokens > max_tokens:
            break
        
        context_parts.append(
            f"## Source: {chunk['source']}\n"
            f"{chunk['content']}\n"
        )
        current_length += chunk_tokens
    
    return "\n".join(context_parts)
