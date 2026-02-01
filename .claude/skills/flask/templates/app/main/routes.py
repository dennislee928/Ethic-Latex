"""Main blueprint routes."""

from flask import render_template, jsonify
from flask_login import login_required, current_user
from app.main import bp


@bp.route("/")
def index():
    """Home page."""
    return render_template("main/index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard - requires authentication."""
    return render_template("main/dashboard.html", user=current_user)


@bp.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})
