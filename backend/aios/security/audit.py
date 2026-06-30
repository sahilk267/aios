"""AIOS Audit Logging - Comprehensive action logging."""

import json
import os
import sqlite3
import time
import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class AuditLogger:
    """Comprehensive audit logging for all system actions."""

    def __init__(self, db_path: str = "data/sqlite/audit.db"):
        self._db_path = db_path
        self._logger = structlog.get_logger("aios.security.audit")
        self._init_db()

    def _init_db(self) -> None:
        """Initialize audit database."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    user_id TEXT,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def log(
        self,
        action: str,
        user_id: str = "",
        resource: str = "",
        details: dict[str, Any] | None = None,
        ip_address: str = "",
    ) -> str:
        """Log an action.

        Args:
            action: Action performed.
            user_id: User who performed the action.
            resource: Resource affected.
            details: Additional details.
            ip_address: Client IP address.

        Returns:
            Log entry ID.
        """
        entry_id = str(uuid.uuid4())
        now = time.time()

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                INSERT INTO audit_log (id, action, user_id, resource, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id, action, user_id, resource,
                json.dumps(details or {}, default=str),
                ip_address, now,
            ))
            conn.commit()

        return entry_id

    def query(
        self,
        action: str = "",
        user_id: str = "",
        resource: str = "",
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit log entries.

        Args:
            action: Filter by action.
            user_id: Filter by user.
            resource: Filter by resource.
            limit: Maximum results.

        Returns:
            List of audit entries.
        """
        query = "SELECT * FROM audit_log WHERE 1=1"
        params: list = []

        if action:
            query += " AND action = ?"
            params.append(action)
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if resource:
            query += " AND resource = ?"
            params.append(resource)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                {
                    "id": row[0],
                    "action": row[1],
                    "user_id": row[2],
                    "resource": row[3],
                    "details": json.loads(row[4]) if row[4] else {},
                    "ip_address": row[5],
                    "timestamp": row[6],
                }
                for row in rows
            ]


# Global instance
audit_logger = AuditLogger()
