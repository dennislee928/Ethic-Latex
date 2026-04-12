import logging
from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.

    This is intentionally minimal for the PoC; additional settings can be
    added as the application evolves.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "ERH-on-Security API"

    # GitLab configuration
    gitlab_base_url: Optional[AnyUrl] = None
    gitlab_token: Optional[str] = None

    # Database configuration (SQLite for local/dev, PostgreSQL via env in production)
    database_url: str = "sqlite:///./erh_security_app.db"

    # Logging
    log_level: str = "INFO"

    # CORS: comma-separated list of allowed origins.
    # Example: "http://localhost:3000,https://app.example.com"
    # Defaults to localhost:3000 for local development only.
    cors_allowed_origins: str = "http://localhost:3000"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance so we only load from environment once.
    """
    settings = Settings()

    # Basic logging configuration
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logging.getLogger(__name__).info("Settings loaded, log level=%s", settings.log_level)
    return settings

