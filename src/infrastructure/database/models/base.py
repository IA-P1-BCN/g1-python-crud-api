"""Base compartida por todos los modelos de persistencia."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarativa de los modelos SQLAlchemy."""
