"""AIOS Provider Registry - Provider management and routing.

This module manages AI provider registration, selection, and routing.
"""

from typing import Any, Optional

import structlog

from aios.providers.base import BaseProvider, ProviderConfig

logger = structlog.get_logger(__name__)


class ProviderRegistry:
    """Registry for managing AI providers.

    Handles provider registration, instantiation, and selection
    based on capabilities and availability.
    """

    _instance: Optional["ProviderRegistry"] = None
    _provider_classes: dict[str, type[BaseProvider]] = {}
    _active_providers: dict[str, BaseProvider] = {}

    def __new__(cls) -> "ProviderRegistry":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, provider_class: type[BaseProvider]) -> type[BaseProvider]:
        """Register a provider class.

        Args:
            provider_class: The provider class to register.

        Returns:
            The registered class.
        """
        name = provider_class.PROVIDER_NAME
        cls._provider_classes[name] = provider_class
        logger.info("Provider registered", name=name)
        return provider_class

    @classmethod
    def create_provider(
        cls,
        name: str,
        config: ProviderConfig,
    ) -> BaseProvider:
        """Create a provider instance.

        Args:
            name: Provider name (e.g., 'ollama', 'openrouter').
            config: Provider configuration.

        Returns:
            Provider instance.

        Raises:
            ValueError: If provider is not registered.
        """
        provider_class = cls._provider_classes.get(name)
        if provider_class is None:
            available = ", ".join(cls._provider_classes.keys())
            raise ValueError(
                f"Unknown provider: '{name}'. Available: {available}"
            )

        provider = provider_class(config)
        cls._active_providers[provider.config.name] = provider
        logger.info("Provider created", name=name, config_name=config.name)
        return provider

    @classmethod
    def get_provider(cls, name: str) -> BaseProvider | None:
        """Get an active provider by config name.

        Args:
            name: The provider config name.

        Returns:
            Provider instance or None.
        """
        return cls._active_providers.get(name)

    @classmethod
    def list_providers(cls) -> list[dict[str, Any]]:
        """List all registered providers.

        Returns:
            List of provider metadata.
        """
        return [
            {
                "name": name,
                "class": provider_class.__name__,
                "default_model": provider_class.DEFAULT_MODEL,
                "supports_streaming": provider_class.SUPPORTS_STREAMING,
            }
            for name, provider_class in cls._provider_classes.items()
        ]

    @classmethod
    def get_active_providers(cls) -> list[dict[str, Any]]:
        """Get all active provider instances.

        Returns:
            List of provider states.
        """
        return [p.get_metrics() for p in cls._active_providers.values()]

    @classmethod
    async def get_healthy_provider(
        cls,
        preferred: str | None = None,
    ) -> BaseProvider | None:
        """Get a healthy provider, optionally preferring a specific one.

        Args:
            preferred: Preferred provider name.

        Returns:
            A healthy provider instance, or None.
        """
        # Try preferred first
        if preferred:
            provider = cls._active_providers.get(preferred)
            if provider and await provider.health_check():
                return provider

        # Try all providers
        for name, provider in cls._active_providers.items():
            if name == preferred:
                continue
            if await provider.health_check():
                return provider

        return None
