"""Engine y sesión de SQLAlchemy para MySQL."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session]:
    """Dependencia que ofrece una sesión y la cierra al terminar."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
