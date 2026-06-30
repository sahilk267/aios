"""AIOS OpenRouter Provider - Free tier AI model provider.

This module provides integration with OpenRouter for accessing free AI models.
"""

import structlog
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from aios.providers.base import (
    BaseProvider,
    ProviderConfig,
    ProviderResponse,
    ProviderStatus,
)

logger = structlog.get_logger(__name__)

# Free models available on OpenRouter
FREE_MODELS = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "-2-7b-instruct:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    "mistralai/mistral-7b-instruct:free",
]


class OpenRouterProvider(BaseProvider):
    """Provider for OpenRouter free tier models.

    Provides access to free AI models through the OpenRouter API.
    Requires a free API key from https://openrouter.ai/
    """

    PROVIDER_NAME = "openrouter"
    DEFAULT_MODEL = "google/gemma-2-9b-it:free"
    SUPPORTS_STREAMING = True

    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(
                name="openrouter",
                base_url="https://openrouter.ai/api/v1",
                default_model=self.DEFAULT_MODEL,
            )
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        headers.update(self.config.extra_headers)
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=self._get_headers(),
                timeout=self.config.timeout,
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Generate a completion using OpenRouter."""
        client = await self._get_client()
        model = model or self.config.default_model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "stream": False,
        }

        self._logger.debug("OpenRouter generate request", model=model)
        start_time = time.time()

        try:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            duration_ms = (time.time() - start_time) * 1000
            choice = data["choices"][0]

            return ProviderResponse(
                content=choice["message"]["content"],
                model=model,
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                total_tokens=data.get("usage", {}).get("total_tokens", 0),
                duration_ms=duration_ms,
                metadata={"finish_reason": choice.get("finish_reason")},
            )
        except httpx.HTTPError as e:
            self.status = ProviderStatus.ERROR
            self._logger.error("OpenRouter request failed", error=str(e))
            raise

    async def stream_generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """Stream a completion using OpenRouter."""
        client = await self._get_client()
        model = model or self.config.default_model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "stream": True,
        }

        self._logger.debug("OpenRouter stream request", model=model)

        try:
            async with client.stream(
                "POST", "/chat/completions", json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk.strip() == "[DONE]":
                            break
                        import json
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except httpx.HTTPError as e:
            self.status = ProviderStatus.ERROR
            self._logger.error("OpenRouter stream failed", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if OpenRouter API is reachable."""
        try:
            client = await self._get_client()
            response = await client.get("/models")
            if response.status_code == 200:
                self.status = ProviderStatus.CONNECTED
                return True
        except Exception:
            pass

        self.status = ProviderStatus.ERROR
        return False

    async def list_models(self) -> List[str]:
        """List available free models."""
        return FREE_MODELS.copy()

    @staticmethod
    def get_free_models() -> List[str]:
        """Get list of free models.

        Returns:
            List of free model identifiers.
        """
        return FREE_MODELS.copy()
