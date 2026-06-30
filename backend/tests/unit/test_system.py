"""Tests for system endpoints."""

from fastapi.testclient import TestClient

from aios.main import app


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self):
        """Test basic health check."""
        client = TestClient(app)
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_system_info(self):
        """Test system info endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/info")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AIOS"
        assert "version" in data
        assert "features" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AIOS"
        assert "docs" in data
