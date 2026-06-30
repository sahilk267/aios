"""AIOS Graph Memory Store (NetworkX)."""

import structlog
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from aios.core.config import settings

logger = structlog.get_logger(__name__)

# Global graph instance
graph = None
GRAPH_FILE = "data/graph/aios_graph.gpickle"


async def init_graph_store() -> None:
    """Initialize the graph store."""
    global graph
    
    try:
        import networkx as nx
        
        graph = nx.DiGraph()
        
        # Load from file if exists
        graph_path = Path(GRAPH_FILE)
        if graph_path.exists():
            graph = nx.read_gpickle(str(graph_path))
            logger.info("Graph store loaded from file", nodes=graph.number_of_nodes())
        else:
            logger.info("New graph store created")
        
    except Exception as e:
        logger.error("Failed to initialize graph store", error=str(e))
        raise


async def check_graph_store_health() -> bool:
    """Check graph store health."""
    return graph is not None


async def save_graph() -> None:
    """Persist graph to disk."""
    global graph
    
    if graph is None:
        return
    
    try:
        import networkx as nx
        from pathlib import Path
        
        graph_path = Path(GRAPH_FILE)
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        nx.write_gpickle(graph, str(graph_path))
    except Exception as e:
        logger.error("Failed to save graph", error=str(e))


async def add_node(
    node_id: str,
    node_type: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Add a node to the graph."""
    global graph
    
    if graph is None:
        raise RuntimeError("Graph store not initialized")
    
    graph.add_node(node_id, type=node_type, **(data or {}))
    await save_graph()


async def add_edge(
    source_id: str,
    target_id: str,
    relation: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Add an edge to the graph."""
    global graph
    
    if graph is None:
        raise RuntimeError("Graph store not initialized")
    
    graph.add_edge(source_id, target_id, relation=relation, **(data or {}))
    await save_graph()


async def get_neighbors(
    node_id: str,
    direction: str = "out",
    relation: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get neighbors of a node."""
    global graph
    
    if graph is None:
        raise RuntimeError("Graph store not initialized")
    
    neighbors = []
    
    if direction in ("out", "both"):
        for _, target, data in graph.out_edges(node_id, data=True):
            if relation is None or data.get("relation") == relation:
                neighbors.append({"node": target, "data": data, "direction": "out"})
    
    if direction in ("in", "both"):
        for source, _, data in graph.in_edges(node_id, data=True):
            if relation is None or data.get("relation") == relation:
                neighbors.append({"node": source, "data": data, "direction": "in"})
    
    return neighbors


async def find_path(
    source_id: str,
    target_id: str,
    max_depth: int = 5,
) -> Optional[List[str]]:
    """Find a path between two nodes."""
    global graph
    
    if graph is None:
        raise RuntimeError("Graph store not initialized")
    
    try:
        import networkx as nx
        path = nx.shortest_path(graph, source_id, target_id)
        if len(path) <= max_depth + 1:
            return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        pass
    
    return None


async def query_nodes(
    node_type: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Query nodes by type and filters."""
    global graph
    
    if graph is None:
        raise RuntimeError("Graph store not initialized")
    
    results = []
    for node_id, data in graph.nodes(data=True):
        if node_type and data.get("type") != node_type:
            continue
        
        if filters:
            match = all(data.get(k) == v for k, v in filters.items())
            if not match:
                continue
        
        results.append({"id": node_id, **data})
    
    return results
