"""Smoke test to verify basic application functionality."""


def test_health_endpoint(client):
    """Test that the health check endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_connection(db_session):
    """Test that database session is available."""
    from sqlalchemy import text
    # Simple query to verify database connectivity
    result = db_session.execute(text("SELECT 1 as value"))
    row = result.fetchone()
    assert row is not None
    assert row[0] == 1
