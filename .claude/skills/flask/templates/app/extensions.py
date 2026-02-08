"""Flask extensions initialization.

Extensions are initialized without app binding here to avoid circular imports.
They are bound to the app in the application factory (create_app).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Database
db = SQLAlchemy()

# Login manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"
