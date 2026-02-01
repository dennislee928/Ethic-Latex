from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from ..config import get_settings


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    """


def get_engine():
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    # PostgreSQL uses connection pooling by default, no special args needed
    return create_engine(
        settings.database_url,
        connect_args=connect_args,
        pool_pre_ping=True,  # Verify connections before using
    )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for providing a SQLAlchemy Session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


