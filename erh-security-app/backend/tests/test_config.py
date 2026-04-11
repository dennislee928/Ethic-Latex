from app.config import Settings


def test_default_database_url_uses_sqlite_for_local_development(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)

    assert settings.database_url.startswith("sqlite:///")
