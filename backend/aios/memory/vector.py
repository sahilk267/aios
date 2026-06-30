"""AIOS Vector Memory Store (Qdrant)."""

import structlog
from typing import Any, Dict, List, Optional

from aios.core.config import settings

logger = structlog.get_logger(__name__)

# Global Qdrant client
qdrant_client = None
COLLECTION_NAME = "aios_vectors"


async def init_vector_store() -> None:
    """Initialize the vector store connection."""
    global qdrant_client
    
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        if settings.qdrant_url:
            qdrant_client = QdrantClient(url=settings.qdrant_url)
        else:
            qdrant_client = QdrantClient(path=settings.qdrant_path)
        
        # Create collection if it doesn't exist
        collections = qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if COLLECTION_NAME not in collection_names:
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 dimension
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection", collection=COLLECTION_NAME)
        
        logger.info("Vector store initialized")
    except Exception as e:
        logger.error("Failed to initialize vector store", error=str(e))
        raise


async def check_vector_store_health() -> bool:
    """Check vector store health."""
    if qdrant_client is None:
        return False
    
    try:
        qdrant_client.get_collections()
        return True
    except Exception as e:
        logger.error("Vector store health check failed", error=str(e))
        return False


async def upsert_vector(
    id: str,
    vector: List[float],
    payload: Dict[str, Any],
) -> None:
    """Insert or update a vector in the store."""
    if qdrant_client is None:
        raise RuntimeError("Vector store not initialized")
    
    from qdrant_client.models import PointStruct
    
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=id, vector=vector, payload=payload)],
    )


async def search_vectors(
    query_vector: List[float],
    limit: int = 10,
    score_threshold: float = 0.7,
    filter_conditions: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Search for similar vectors."""
    if qdrant_client is None:
        raise RuntimeError("Vector store not initialized")
    
    from qdrant_client.models import Filter
    
    search_filter = None
    if filter_conditions:
        from qdrant_client.models import FieldCondition, MatchValue
        must_conditions = []
        for key, value in filter_conditions.items():
            must_conditions.append(
                FieldCondition(key=key, match=MatchValue(value=value))
            )
        search_filter = Filter(must=must_conditions)
    
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit,
        score_threshold=score_threshold,
        query_filter=search_filter,
    )
    
    return [
        {
            "id": str(r.id),
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


async def delete_vector(id: str) -> None:
    """Delete a vector from the store."""
    if qdrant_client is None:
        raise RuntimeError("Vector store not initialized")
    
    from qdrant_client.models import PointIdsList
    
    qdrant_client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=PointIdsList(points=[id]),
    )
