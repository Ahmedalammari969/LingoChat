"""
LinguaChat — User ORM Model

Schema defined in: docs/database-schema.md § 1. users
Implementation: Yousef Khairy — TASK: Database
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    """
    Represents a registered LinguaChat user.

    SECURITY: hashed_password stores ONLY bcrypt hash. NEVER plaintext.
    See docs/security.md § 2. Password Hashing.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    preferred_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    # Defined on related models to avoid circular imports at foundation stage.
    # rooms_created = relationship("Room", back_populates="creator")
    # room_memberships = relationship("RoomMember", back_populates="user")
    # messages_sent = relationship("Message", back_populates="sender")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
