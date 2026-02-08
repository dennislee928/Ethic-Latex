"""Tests for authentication routes."""


def test_register_page(client):
    """Test registration page loads."""
    response = client.get("/auth/register")
    assert response.status_code == 200


def test_login_page(client):
    """Test login page loads."""
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_register_user(client):
    """Test user registration."""
    response = client.post("/auth/register", data={
        "email": "new@example.com",
        "password": "testpass123",
        "confirm": "testpass123",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_user(client, user):
    """Test user login."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "testpassword123",
    }, follow_redirects=True)
    assert response.status_code == 200


def test_login_invalid_password(client, user):
    """Test login with wrong password."""
    response = client.post("/auth/login", data={
        "email": "test@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data
