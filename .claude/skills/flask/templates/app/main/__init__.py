"""Main blueprint."""

from flask import Blueprint

bp = Blueprint("main", __name__)

# Import routes after bp is created to avoid circular imports
from app.main import routes  # noqa: F401, E402
