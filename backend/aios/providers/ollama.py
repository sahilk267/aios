"""AIOS Ollama Provider - Local AI model provider.

This module provides integration with Ollama for running AI models locally.
"""

import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import structlog

from aios.providers.base import (
    BaseProvider,
    ProviderConfig,
    ProviderResponse,
    ProviderStatus,
)

logger = structlog.get_logger(__name__)


class OllamaProvider(BaseProvider):
    """Provider for Ollama local AI models.

    Supports any model available in your Ollama installation.
    No API key required - runs entirely locally.
    """

    PROVIDER_NAME = "ollama"
    DEFAULT_MODEL = "llama3"
    SUPPORTS_STREAMING = True

    def __init__(self, config: ProviderConfig | None = None):
        if config is None:
            config = ProviderConfig(
                name="ollama-local",
                base_url="http://localhost:11434",
                default_model="llama3",
            )
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion using Ollama."""
        client = await self._get_client()
        model = model or self.config.default_model

        options = {
            "temperature": temperature or self.config.temperature,
        }
        if max_tokens:
            options["num_predict"] = max_tokens

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options,
        }
        if system_prompt:
            payload["system"] = system_prompt

        self._logger.debug("Ollama generate request", model=model)
        start_time = time.time()

        try:
            response = await client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

            duration_ms = (time.time() - start_time) * 1000

            return ProviderResponse(
                content=data.get("response", ""),
                model=model,
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=(
                    data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                ),
                duration_ms=duration_ms,
                metadata={
                    "total_duration": data.get("total_duration", 0),
                    "load_duration": data.get("load_duration", 0),
                },
            )
        except httpx.HTTPError as e:
            self.status = ProviderStatus.ERROR
            self._logger.exception("Ollama request failed", error=str(e))
            raise

    async def stream_generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion using Ollama."""
        client = await self._get_client()
        model = model or self.config.default_model

        options = {
            "temperature": temperature or self.config.temperature,
        }
        if max_tokens:
            options["num_predict"] = max_tokens

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": options,
        }
        if system_prompt:
            payload["system"] = system_prompt

        self._logger.debug("Ollama stream request", model=model)

        try:
            async with client.stream(
                "POST", "/api/generate", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPError as e:
            self.status = ProviderStatus.ERROR
            self._logger.exception("Ollama stream failed", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            if response.status_code == 200:
                self.status = ProviderStatus.CONNECTED
                return True
        except Exception:
            pass

        self.status = ProviderStatus.ERROR
        return False

    async def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            self._logger.exception("Failed to list models", error=str(e))
            return [self.config.default_model]

    async def pull_model(self, model: str) -> bool:
        """Pull a model from Ollama library.

        Args:
            model: Model name to pull.

        Returns:
            True if successful.
        """
        try:
            client = await self._get_client()
            response = await client.post(
                "/api/pull",
                json={"name": model},
                timeout=600,  # 10 minutes for model download
            )
            response.raise_for_status()
            self._logger.info("Model pulled successfully", model=model)
            return True
        except Exception as e:
            self._logger.exception("Failed to pull model", model=model, error=str(e))
            return False
