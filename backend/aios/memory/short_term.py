"""AIOS Short-Term Memory Store.

Fast in-memory storage with TTL for temporary context.
"""

import time
from collections import OrderedDict
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ShortTermStore:
    """In-memory key-value store with TTL support.

    Automatically expires entries after a configurable time.
    Uses LRU eviction when capacity is reached.
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._store: OrderedDict[str, Any] = OrderedDict()
        self._expiry: dict[str, float] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._logger = structlog.get_logger("aios.memory.short_term")

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value with optional TTL.

        Args:
            key: Storage key.
            value: Value to store.
            ttl: Time-to-live in seconds (uses default if None).
        """
        if key in self._store:
            del self._store[key]
        elif len(self._store) >= self._max_size:
            self._evict_oldest()

        self._store[key] = value
        self._expiry[key] = time.time() + (ttl or self._default_ttl)

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value by key.

        Args:
            key: Storage key.
            default: Default value if key not found or expired.

        Returns:
            Stored value or default.
        """
        self._cleanup_expired()

        if key in self._store:
            self._store.move_to_end(key)
            return self._store[key]
        return default

    def delete(self, key: str) -> bool:
        """Delete a key from the store.

        Args:
            key: Key to delete.

        Returns:
            True if key existed and was deleted.
        """
        if key in self._store:
            del self._store[key]
            del self._expiry[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries."""
        self._store.clear()
        self._expiry.clear()

    def keys(self) -> list[str]:
        """Get all non-expired keys."""
        self._cleanup_expired()
        return list(self._store.keys())

    def size(self) -> int:
        """Get current number of entries."""
        self._cleanup_expired()
        return len(self._store)

    def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = time.time()
        expired = [k for k, exp in self._expiry.items() if exp <= now]
        for key in expired:
            del self._store[key]
            del self._expiry[key]

    def _evict_oldest(self) -> None:
        """Evict the oldest entry (LRU)."""
        if self._store:
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
            del self._expiry[oldest_key]


# Global instance
short_term_store = ShortTermStore()
