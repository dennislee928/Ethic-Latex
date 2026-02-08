"""Pytest fixtures for Flask testing."""

import pytest
from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    """Create a test user."""
    with app.app_context():
        user = User(email="test@example.com")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()
        return user
