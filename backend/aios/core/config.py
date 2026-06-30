"""AIOS Configuration Management."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AIOS"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    secret_key: str = "dev-secret-key-change-in-production"

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: bool | str | int | None) -> bool:
        """Parse debug value from various types."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        if isinstance(v, int):
            return bool(v)
        return False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    db_path: str = "data/sqlite/aios.db"
    postgres_url: str | None = None

    # Redis
    redis_url: str | None = None

    # Qdrant
    qdrant_path: str = "data/qdrant"
    qdrant_url: str | None = None

    # Neo4j
    neo4j_url: str | None = None
    neo4j_user: str = "neo4j"
    neo4j_password: str = "aios12345"

    # OpenSearch
    opensearch_url: str | None = None

    # Ollama
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # OpenRouter
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # LiteLLM
    litellm_url: str | None = None

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Indexing
    index_chunk_size: int = 1000
    index_chunk_overlap: int = 200
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        if self.postgres_url:
            return self.postgres_url
        return f"sqlite+aiosqlite:///{self.db_path}"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
