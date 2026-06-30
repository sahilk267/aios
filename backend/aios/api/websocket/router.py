"""AIOS WebSocket Router."""

import structlog
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = structlog.get_logger(__name__)

ws_router = APIRouter()

# Connected WebSocket clients
_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections."""
    
    async def connect(self, websocket: WebSocket, channel: str = "default"):
        """Accept a connection and add to channel."""
        await websocket.accept()
        if channel not in _connections:
            _connections[channel] = set()
        _connections[channel].add(websocket)
        logger.info("WebSocket connected", channel=channel)
    
    def disconnect(self, websocket: WebSocket, channel: str = "default"):
        """Remove a connection from channel."""
        if channel in _connections:
            _connections[channel].discard(websocket)
            if not _connections[channel]:
                del _connections[channel]
        logger.info("WebSocket disconnected", channel=channel)
    
    async def broadcast(self, message: dict, channel: str = "default"):
        """Broadcast a message to all connections in a channel."""
        if channel not in _connections:
            return
        
        disconnected = set()
        for connection in _connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn, channel)


manager = ConnectionManager()


@ws_router.websocket("/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for real-time events."""
    await manager.connect(websocket, "events")
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for now (will be replaced with proper event handling)
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "events")


@ws_router.websocket("/agents/{agent_id}")
async def websocket_agent(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent-specific events."""
    await manager.connect(websocket, f"agent:{agent_id}")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "agent_update", "agent_id": agent_id, "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"agent:{agent_id}")
