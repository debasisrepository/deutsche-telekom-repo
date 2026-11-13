"""Smoke test - verifies basic application startup and health endpoints."""


def test_health_endpoint(client):
    """Test the health endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ready_endpoint(client):
    """Test the readiness endpoint checks database connectivity."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_app_starts_without_error(client):
    """Test that the FastAPI application starts successfully."""
    # If we can create the client, the app started
    assert client is not None
