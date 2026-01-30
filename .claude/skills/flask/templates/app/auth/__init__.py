"""Auth blueprint."""

from flask import Blueprint

bp = Blueprint("auth", __name__)

# Import routes after bp is created to avoid circular imports
from app.auth import routes  # noqa: F401, E402
