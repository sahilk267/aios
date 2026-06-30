"""AIOS BaseProvider - Abstract AI provider interface.

This module defines the common interface that all AI providers must implement,
ensuring consistent behavior across different model backends.
"""

import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class ProviderStatus(Enum):
    """Provider connection status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ProviderConfig:
    """Configuration for an AI provider."""

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str | None = None,
        default_model: str = "llama3",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 120,
        extra_headers: dict[str, str] | None = None,
    ):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.default_model = default_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.extra_headers = extra_headers or {}


class ProviderResponse:
    """Response from an AI provider."""

    def __init__(
        self,
        content: str,
        model: str,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        duration_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.content = content
        self.model = model
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.duration_ms = duration_ms
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class BaseProvider(ABC):
    """Abstract base class for AI providers.

    All AI providers must inherit from this class and implement
    the generate and stream_generate methods.
    """

    PROVIDER_NAME: str = "base"
    DEFAULT_MODEL: str = "llama3"
    SUPPORTS_STREAMING: bool = False

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.status = ProviderStatus.DISCONNECTED
        self._logger = structlog.get_logger(
            "aios.provider",
            provider=self.PROVIDER_NAME,
            name=config.name,
        )

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion for the given prompt.

        Args:
            prompt: The user prompt.
            model: Model override.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            system_prompt: System prompt for the model.
            **kwargs: Additional provider-specific parameters.

        Returns:
            ProviderResponse with the generated content.
        """
        ...

    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion for the given prompt.

        Args:
            prompt: The user prompt.
            model: Model override.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            system_prompt: System prompt for the model.
            **kwargs: Additional provider-specific parameters.

        Yields:
            Chunks of generated text.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is reachable and healthy.

        Returns:
            True if the provider is healthy.
        """
        ...

    async def list_models(self) -> list[str]:
        """List available models from this provider.

        Returns:
            List of model identifiers.
        """
        return [self.config.default_model]

    def get_metrics(self) -> dict[str, Any]:
        """Get provider metrics.

        Returns:
            Dictionary of provider metrics.
        """
        return {
            "provider": self.PROVIDER_NAME,
            "name": self.config.name,
            "status": self.status.value,
            "base_url": self.config.base_url,
            "default_model": self.config.default_model,
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name={self.config.name} "
            f"status={self.status.value}>"
        )
