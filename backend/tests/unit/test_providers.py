"""Tests for provider system."""

import pytest
from aios.providers.base import (
    BaseProvider,
    ProviderConfig,
    ProviderResponse,
    ProviderStatus,
)
from aios.providers.ollama import OllamaProvider
from aios.providers.openrouter import OpenRouterProvider, FREE_MODELS
from aios.providers.registry import ProviderRegistry


class TestProviderConfig:
    """Test ProviderConfig class."""

    def test_create_config(self):
        """Test config creation."""
        config = ProviderConfig(
            name="test",
            base_url="http://localhost:11434",
            default_model="llama3",
        )
        assert config.name == "test"
        assert config.base_url == "http://localhost:11434"
        assert config.default_model == "llama3"
        assert config.temperature == 0.7

    def test_config_defaults(self):
        """Test config defaults."""
        config = ProviderConfig(name="test", base_url="http://test")
        assert config.max_tokens == 4096
        assert config.timeout == 120
        assert config.extra_headers == {}


class TestProviderResponse:
    """Test ProviderResponse class."""

    def test_create_response(self):
        """Test response creation."""
        response = ProviderResponse(
            content="Hello world",
            model="llama3",
            prompt_tokens=10,
            completion_tokens=20,
        )
        assert response.content == "Hello world"
        assert response.model == "llama3"
        assert response.total_tokens == 30

    def test_response_to_dict(self):
        """Test response serialization."""
        response = ProviderResponse(content="test", model="llama3")
        d = response.to_dict()
        assert d["content"] == "test"
        assert d["model"] == "llama3"
        assert "id" in d


class TestOllamaProvider:
    """Test OllamaProvider class."""

    def test_create_provider(self):
        """Test provider creation."""
        provider = OllamaProvider()
        assert provider.PROVIDER_NAME == "ollama"
        assert provider.DEFAULT_MODEL == "llama3"
        assert provider.SUPPORTS_STREAMING is True

    def test_custom_config(self):
        """Test provider with custom config."""
        config = ProviderConfig(
            name="custom-ollama",
            base_url="http://custom:11434",
            default_model="codellama",
        )
        provider = OllamaProvider(config)
        assert provider.config.name == "custom-ollama"
        assert provider.config.default_model == "codellama"

    def test_get_metrics(self):
        """Test metrics collection."""
        provider = OllamaProvider()
        metrics = provider.get_metrics()
        assert metrics["provider"] == "ollama"
        assert "status" in metrics


class TestOpenRouterProvider:
    """Test OpenRouterProvider class."""

    def test_create_provider(self):
        """Test provider creation."""
        provider = OpenRouterProvider()
        assert provider.PROVIDER_NAME == "openrouter"
        assert provider.SUPPORTS_STREAMING is True

    def test_free_models(self):
        """Test free models list."""
        assert len(FREE_MODELS) > 0
        assert all(":free" in m for m in FREE_MODELS)

    def test_get_free_models(self):
        """Test static method for free models."""
        models = OpenRouterProvider.get_free_models()
        assert models == FREE_MODELS


class TestProviderRegistry:
    """Test ProviderRegistry class."""

    def test_register_provider(self):
        """Test provider registration."""
        registry = ProviderRegistry()
        providers = registry.list_providers()
        assert len(providers) >= 2
        names = [p["name"] for p in providers]
        assert "ollama" in names
        assert "openrouter" in names

    def test_create_provider(self):
        """Test creating provider instance."""
        registry = ProviderRegistry()
        config = ProviderConfig(
            name="test-ollama",
            base_url="http://localhost:11434",
        )
        provider = registry.create_provider("ollama", config)
        assert isinstance(provider, OllamaProvider)

    def test_create_unknown_provider(self):
        """Test creating unknown provider raises error."""
        registry = ProviderRegistry()
        config = ProviderConfig(name="test", base_url="http://test")
        with pytest.raises(ValueError, match="Unknown provider"):
            registry.create_provider("unknown", config)

    def test_get_active_providers(self):
        """Test getting active providers."""
        registry = ProviderRegistry()
        active = registry.get_active_providers()
        assert isinstance(active, list)
