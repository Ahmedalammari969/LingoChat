"""
LinguaChat — SQLAlchemy Declarative Base

All ORM models must inherit from Base defined here.
Schema Source of Truth: docs/database-schema.md
Implementation: Yousef Khairy — TASK-01-YOUSEF
"""

from datetime import datetime, timezone
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all LinguaChat ORM models.
    All models inherit from this class.
    """
    pass


def utcnow() -> datetime:
    """Return current UTC time with timezone awareness. Used as column defaults."""
    return datetime.now(timezone.utc)
