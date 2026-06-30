"""AIOS Approval Gates - Human-in-the-loop approval workflow."""

import structlog
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = structlog.get_logger(__name__)


class ApprovalStatus(Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalRequest:
    """Represents an approval request."""

    def __init__(
        self,
        title: str,
        description: str,
        requester: str,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_hours: int = 24,
    ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.requester = requester
        self.metadata = metadata or {}
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.utcnow()
        self.timeout_hours = timeout_hours
        self.resolved_at: Optional[datetime] = None
        self.resolution = ""

    def approve(self, resolution: str = "") -> None:
        """Approve the request."""
        self.status = ApprovalStatus.APPROVED
        self.resolved_at = datetime.utcnow()
        self.resolution = resolution

    def reject(self, resolution: str = "") -> None:
        """Reject the request."""
        self.status = ApprovalStatus.REJECTED
        self.resolved_at = datetime.utcnow()
        self.resolution = resolution

    def is_expired(self) -> bool:
        """Check if request has expired."""
        if self.status != ApprovalStatus.PENDING:
            return False
        elapsed = (datetime.utcnow_at).total_seconds()
        return elapsed > (self.timeout_hours * 3600)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "requester": self.requester,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution": self.resolution,
        }


class ApprovalGate:
    """Manages approval gates for workflow execution."""

    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._logger = structlog.get_logger("aios.engine.approval")

    def create_request(
        self,
        title: str,
        description: str,
        requester: str,
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """Create a new approval request."""
        request = ApprovalRequest(
            title=title,
            description=description,
            requester=requester,
            metadata=metadata,
        )
        self._requests[request.id] = request
        if callback:
            self._callbacks[request.id] = callback
        self._logger.info("Approval request created", request_id=request.id, title=title)
        return request

    def approve(self, request_id: str, resolution: str = "") -> bool:
        """Approve a request."""
        request = self._requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        request.approve(resolution)
        self._execute_callback(request)
        return True

    def reject(self, request_id: str, resolution: str = "") -> bool:
        """Reject a request."""
        request = self._requests.get(request_id)
        if not request or request.status != ApprovalStatus.PENDING:
            return False
        request.reject(resolution)
        self._execute_callback(request)
        return True

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a request by ID."""
        return self._requests.get(request_id)

    def get_pending(self) -> List[ApprovalRequest]:
        """Get all pending requests."""
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]

    def _execute_callback(self, request: ApprovalRequest) -> None:
        """Execute callback for a resolved request."""
        callback = self._callbacks.get(request.id)
        if callback:
            try:
                callback(request)
            except Exception as e:
                self._logger.error("Callback error", error=str(e))


# Global instance
approval_gate = ApprovalGate()
