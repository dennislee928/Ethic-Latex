"""Application factory for Flask app."""

from flask import Flask
from config import config
from app.extensions import db, login_manager


def create_app(config_name="default"):
    """Create and configure the Flask application.

    Args:
        config_name: Configuration to use (development, testing, production)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.main import bp as main_bp
    from app.auth import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
