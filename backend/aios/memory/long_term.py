"""AIOS Long-Term Memory Store.

Persistent storage backed by SQLite for durable memory.
"""

import structlog
import json
import time
import os
import sqlite3
from typing import Any, Dict, List, Optional

logger = structlog.get_logger(__name__)


class LongTermStore:
    """SQLite-backed persistent key-value store."""

    def __init__(self, db_path: str = "data/sqlite/memory.db"):
        self._db_path = db_path
        self._logger = structlog.get_logger("aios.memory.long_term")
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database table."""
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()

    def set(self, key: str, value: Any) -> None:
        """Store a value persistently."""
        now = time.time()
        serialized = json.dumps(value, default=str)

        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO long_term_memory (key, value, created_at, updated_at)
                VALUES (?, ?, COALESCE((SELECT created_at FROM long_term_memory WHERE key = ?), ?), ?)
            """, (key, serialized, key, now, now))
            conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key."""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT value FROM long_term_memory WHERE key = ?", (key,)
            ).fetchone()
            if row:
                return json.loads(row[0])
        return default

    def delete(self, key: str) -> bool:
        """Delete a key."""
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM long_term_memory WHERE key = ?", (key,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys, optionally filtered by pattern."""
        with sqlite3.connect(self._db_path) as conn:
            if pattern:
                rows = conn.execute(
                    "SELECT key FROM long_term_memory WHERE key LIKE ?",
                    (pattern,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT key FROM long_term_memory"
                ).fetchall()
            return [row[0] for row in rows]

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for entries containing the query string."""
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                "SELECT key, value FROM long_term_memory WHERE value LIKE ?",
                (f"%{query}%",)
            ).fetchall()
            return [{"key": row[0], "value": json.loads(row[1])} for row in rows]

    def clear(self) -> None:
        """Clear all entries."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM long_term_memory")
            conn.commit()

    def size(self) -> int:
        """Get number of stored entries."""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM long_term_memory"
            ).fetchone()
            return row[0] if row else 0


# Global instance
long_term_store = LongTermStore()
