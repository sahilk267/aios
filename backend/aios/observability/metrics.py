"""AIOS Metrics Collection - Prometheus-compatible metrics."""

import structlog
import time
from typing import Any, Dict, List, Optional

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Collects and exposes system metrics."""

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        self._logger = structlog.get_logger("aios.observability.metrics")

    def increment(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        key = self._format_key(name, labels)
        self._counters[key] = self._counters.get(key, 0) + value

    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        key = self._format_key(name, labels)
        self._gauges[key] = value

    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram observation."""
        key = self._format_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)

    def get_prometheus_format(self) -> str:
        """Export metrics in Prometheus format."""
        lines: List[str] = []

        for key, value in self._counters.items():
            lines.append(f"{key} {value}")

        for key, value in self._gauges.items():
            lines.append(f"{key} {value}")

        for key, values in self._histograms.items():
            if values:
                lines.append(f"{key}_count {len(values)}")
                lines.append(f"{key}_sum {sum(values)}")
                lines.append(f"{key}_avg {sum(values) / len(values)}")

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get all metrics as dictionary."""
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: {"count": len(v), "sum": sum(v)} for k, v in self._histograms.items()},
        }

    def _format_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Format metric key with labels."""
        if labels:
            label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
            return f"{name}{{{label_str}}}"
        return name


# Global instance
metrics_collector = MetricsCollector()
