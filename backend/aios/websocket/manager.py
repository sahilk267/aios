"""AIOS WebSocket Connection Manager.

Manages real-time WebSocket connections for agent status updates,
workflow progress, and system events.
"""

import json
from datetime import datetime
from enum import Enum
from typing import Any

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class EventType(Enum):
    """Types of WebSocket events."""
    AGENT_STATUS_CHANGED = "agent.status.changed"
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_PROGRESS = "workflow.progress"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    SYSTEM_NOTIFICATION = "system.notification"
    LOG_MESSAGE = "log.message"


class WebSocketEvent:
    """Represents a WebSocket event."""

    def __init__(
        self,
        event_type: EventType,
        data: dict[str, Any],
        channel: str = "default",
    ):
        self.event_type = event_type
        self.data = data
        self.channel = channel
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.event_type.value,
            "data": self.data,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict())


class ConnectionManager:
    """Manages WebSocket connections and event broadcasting."""

    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = {}
        self._client_channels: dict[str, set[str]] = {}
        self._logger = structlog.get_logger("aios.websocket.manager")

    async def connect(
        self,
        websocket: WebSocket,
        channel: str = "default",
        client_id: str | None = None,
    ) -> str:
        """Accept a WebSocket connection and register it.

        Args:
            websocket: The WebSocket connection.
            channel: Channel to subscribe to.
            client_id: Optional client identifier.

        Returns:
            The client ID.
        """
        await websocket.accept()

        if client_id is None:
            client_id = f"client_{id(websocket)}"

        if channel not in self._connections:
            self._connections[channel] = set()
        self._connections[channel].add(websocket)

        if client_id not in self._client_channels:
            self._client_channels[client_id] = set()
        self._client_channels[client_id].add(channel)

        self._logger.info(
            "WebSocket connected",
            client_id=client_id,
            channel=channel,
        )

        return client_id

    def disconnect(
        self,
        websocket: WebSocket,
        channel: str = "default",
        client_id: str | None = None,
    ) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection.
            channel: Channel to unsubscribe from.
            client_id: Optional client identifier.
        """
        if channel in self._connections:
            self._connections[channel].discard(websocket)
            if not self._connections[channel]:
                del self._connections[channel]

        if client_id and client_id in self._client_channels:
            self._client_channels[client_id].discard(channel)
            if not self._client_channels[client_id]:
                del self._client_channels[client_id]

        self._logger.info(
            "WebSocket disconnected",
            client_id=client_id,
            channel=channel,
        )

    async def broadcast(self, event: WebSocketEvent) -> int:
        """Broadcast an event to all connections in a channel.

        Args:
            event: The event to broadcast.

        Returns:
            Number of clients the event was sent to.
        """
        channel = event.channel
        if channel not in self._connections:
            return 0

        disconnected = set()
        sent_count = 0

        for connection in self._connections[channel]:
            try:
                await connection.send_json(event.to_dict())
                sent_count += 1
            except Exception:
                disconnected.add(connection)

        for conn in disconnected:
            self.disconnect(conn, channel)

        return sent_count

    async def send_to_client(
        self,
        client_id: str,
        event: WebSocketEvent,
    ) -> bool:
        """Send an event to a specific client.

        Args:
            client_id: The client ID.
            event: The event to send.

        Returns:
            True if sent successfully.
        """
        channels = self._client_channels.get(client_id, set())
        for channel in channels:
            if channel in self._connections:
                for connection in self._connections[channel]:
                    try:
                        await connection.send_json(event.to_dict())
                        return True
                    except Exception:
                        continue
        return False

    def get_connection_count(self, channel: str = "default") -> int:
        """Get number of active connections in a channel.

        Args:
            channel: The channel to check.

        Returns:
            Number of active connections.
        """
        return len(self._connections.get(channel, set()))

    def get_all_channels(self) -> list[str]:
        """Get list of all active channels.

        Returns:
            List of channel names.
        """
        return list(self._connections.keys())


# Global connection manager instance
ws_manager = ConnectionManager()


async def broadcast_agent_status(
    agent_id: str,
    agent_name: str,
    old_status: str,
    new_status: str,
    task_id: str | None = None,
) -> int:
    """Broadcast agent status change event.

    Args:
        agent_id: Agent identifier.
        agent_name: Agent name.
        old_status: Previous status.
        new_status: New status.
        task_id: Optional task identifier.

    Returns:
        Number of clients notified.
    """
    event = WebSocketEvent(
        event_type=EventType.AGENT_STATUS_CHANGED,
        data={
            "agent_id": agent_id,
            "agent_name": agent_name,
            "old_status": old_status,
            "new_status": new_status,
            "task_id": task_id,
        },
        channel="agents",
    )
    return await ws_manager.broadcast(event)


async def broadcast_workflow_progress(
    workflow_id: str,
    workflow_name: str,
    current_task: str,
    completed_tasks: int,
    total_tasks: int,
) -> int:
    """Broadcast workflow progress event.

    Args:
        workflow_id: Workflow identifier.
        workflow_name: Workflow name.
        current_task: Current task being executed.
        completed_tasks: Number of completed tasks.
        total_tasks: Total number of tasks.

    Returns:
        Number of clients notified.
    """
    event = WebSocketEvent(
        event_type=EventType.WORKFLOW_PROGRESS,
        data={
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "current_task": current_task,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "progress_percent": (
                (completed_tasks / total_tasks * 100)
                if total_tasks > 0
                else 0
            ),
        },
        channel="workflows",
    )
    return await ws_manager.broadcast(event)


async def broadcast_log_message(
    level: str,
    message: str,
    source: str = "system",
) -> int:
    """Broadcast a log message event.

    Args:
        level: Log level (info, warning, error).
        message: Log message.
        source: Log source.

    Returns:
        Number of clients notified.
    """
    event = WebSocketEvent(
        event_type=EventType.LOG_MESSAGE,
        data={
            "level": level,
            "message": message,
            "source": source,
        },
        channel="logs",
    )
    return await ws_manager.broadcast(event)
