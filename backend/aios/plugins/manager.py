"""AIOS Plugin Manager - Plugin lifecycle management."""

import importlib
import importlib.util
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class PluginInfo:
    """Plugin metadata."""

    def __init__(self, name: str, version: str, path: str, description: str = ""):
        self.name = name
        self.version = version
        self.path = path
        self.description = description
        self.loaded = False
        self.instance: Any = None


class PluginManager:
    """Manages plugin discovery, loading, and execution."""

    def __init__(self, plugin_dir: str = "plugins"):
        self._plugin_dir = Path(plugin_dir)
        self[str, PluginInfo] = {}
        self._logger = structlog.get_logger("aios.plugins.manager")

    def discover(self) -> list[PluginInfo]:
        """Discover available plugins."""
        plugins = []
        if not self._plugin_dir.exists():
            return plugins

        for plugin_path in self._plugin_dir.iterdir():
            if plugin_path.is_dir() and (plugin_path / "__init__.py").exists():
                name = plugin_path.name
                plugins.append(PluginInfo(
                    name=name,
                    version="0.1.0",
                    path=str(plugin_path),
                    description=f"Plugin: {name}",
                ))
        return plugins

    def load(self, name: str) -> bool:
        """Load a plugin by name."""
        try:
            spec = importlib.util.spec_from_file_location(
                name, self._plugin_dir / name / "__init__.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._plugins[name] = PluginInfo(
                    name=name,
                    version=getattr(module, "__version__", "0.1.0"),
                    path=str(self._plugin_dir / name),
                    description=getattr(module, "__doc__", ""),
                )
                self._plugins[name].loaded = True
                self._plugins[name].instance = module
                return True
        except Exception as e:
            self._logger.exception("Failed to load plugin", name=name, error=str(e))
        return False

    def unload(self, name: str) -> bool:
        """Unload a plugin."""
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get_loaded(self) -> list[PluginInfo]:
        """Get all loaded plugins."""
        return [p for p in self._plugins.values() if p.loaded]


# Global instance
plugin_manager = PluginManager()
