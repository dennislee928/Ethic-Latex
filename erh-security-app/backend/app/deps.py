from collections.abc import Generator

from sqlalchemy.orm import Session

from .core.db import get_db_session


def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy Session for request handlers.
    """
    yield from get_db_session()


