"""Tests for configuration management."""

from aios.core.config import Settings, get_settings


class TestSettings:
    """Test Settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.app_name == "AIOS"
        assert settings.app_version == "0.1.0"
        assert settings.environment == "development"
        assert settings.port == 8000

    def test_database_url_sqlite(self):
        """Test SQLite database URL generation."""
        settings = Settings()
        assert "sqlite" in settings.database_url

    def test_database_url_postgres(self):
        """Test PostgreSQL database URL when configured."""
        settings = Settings(postgres_url="postgresql://user:pass@localhost/db")
        assert settings.database_url == "postgresql://user:pass@localhost/db"

    def test_is_production(self):
        """Test production environment detection."""
        dev_settings = Settings(environment="development")
        assert not dev_settings.is_production

        prod_settings = Settings(environment="production")
        assert prod_settings.is_production

    def test_cors_origins(self):
        """Test CORS origins default."""
        settings = Settings()
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:5173" in settings.cors_origins


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
