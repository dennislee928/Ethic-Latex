import logging
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables or .env file.

    This is intentionally minimal for the PoC; additional settings can be
    added as the application evolves.
    """

    app_name: str = "ERH-on-Security API"

    # GitLab configuration
    gitlab_base_url: Optional[AnyUrl] = None
    gitlab_token: Optional[str] = None

    # Database configuration (SQLite by default for PoC)
    database_url: str = "sqlite:///./erh_security.db"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


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


