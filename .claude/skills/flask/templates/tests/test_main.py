"""Tests for main routes."""


def test_index(client):
    """Test home page loads."""
    response = client.get("/")
    assert response.status_code == 200


def test_health(client):
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_dashboard_requires_login(client):
    """Test dashboard redirects to login when not authenticated."""
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/auth/login" in response.location
