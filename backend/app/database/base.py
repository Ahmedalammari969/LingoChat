"""
LinguaChat — SQLAlchemy Declarative Base

All ORM models must inherit from Base defined here.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    """
    Shared declarative base for all LinguaChat ORM models.
    All models inherit from this class.
    """
    pass


def utcnow() -> datetime:
    """Return current UTC time. Used as column defaults."""
    return datetime.now(timezone.utc)
