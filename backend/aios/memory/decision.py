"""AIOS Decision Memory Store.

Tracks decisions made by agents with rationale and outcomes.
"""

import json
import os
import sqlite3
import time
import uuid
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class DecisionStore:
    """Stores agent decisions with rationale and outcomes."""

    def __init__(self, db_path: str = "data/sqlite/decisions.db"):
        self._db_path = db_path
        self._logger = structlog.get_logger("aios.memory.decision")
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database table."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    agent_name TEXT,
                    decision_type TEXT NOT NULL,
                    context TEXT,
                    rationale TEXT,
                    outcome TEXT,
                    success INTEGER,
                    created_at REAL NOT NULL
                )
            """)
            conn.commit()

    def record(
        self,
        agent_id: str,
        decision_type: str,
        context: dict[str, Any],
        rationale: str,
        agent_name: str = "",
        outcome: str = "",
        success: bool | None = None,
    ) -> str:
        """Record a decision."""
        decision_id = str(uuid.uuid4())
        now = time.time()

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                INSERT INTO decisions
                (id, agent_id, agent_name, decision_type, context, rationale, outcome, success, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id, agent_id, agent_name, decision_type,
                json.dumps(context, default=str), rationale, outcome,
                1 if success else 0 if success is not None else None,
                now,
            ))
            conn.commit()

        return decision_id

    def get(self, decision_id: str) -> dict[str, Any] | None:
        """Get a decision by ID."""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT * FROM decisions WHERE id = ?", (decision_id,)
            ).fetchone()
            if row:
                return self._row_to_dict(row)
        return None

    def get_by_agent(self, agent_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get decisions by agent."""
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE agent_id = ? ORDER BY created_at DESC LIMIT ?",
                (agent_id, limit)
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_by_type(self, decision_type: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get decisions by type."""
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM decisions WHERE decision_type = ? ORDER BY created_at DESC LIMIT ?",
                (decision_type, limit)
            ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_stats(self) -> dict[str, Any]:
        """Get decision statistics."""
        with sqlite3.connect(self._db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM decisions"
            ).fetchone()[0]
            successful = conn.execute(
                "SELECT COUNT(*) FROM decisions WHERE success = 1"
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM decisions WHERE success = 0"
            ).fetchone()[0]

        return {
            "total_decisions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0,
        }

    def _row_to_dict(self, row) -> dict[str, Any]:
        """Convert a database row to dictionary."""
        return {
            "id": row[0],
            "agent_id": row[1],
            "agent_name": row[2],
            "decision_type": row[3],
            "context": json.loads(row[4]) if row[4] else {},
            "rationale": row[5],
            "outcome": row[6],
            "success": bool(row[7]) if row[7] is not None else None,
            "created_at": row[8],
        }


# Global instance
decision_store = DecisionStore()
