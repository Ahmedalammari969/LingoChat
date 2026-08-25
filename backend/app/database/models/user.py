from __future__ import annotations
"""
LinguaChat — User ORM Model

Schema defined in: docs/database-schema.md § 1. users
Implementation: Yousef Khairy — TASK-01-YOUSEF
"""

import uuid
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, utcnow

if TYPE_CHECKING:
    from app.database.models.room import Room
    from app.database.models.room_member import RoomMember
    from app.database.models.message import Message


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
        default=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    rooms_created: Mapped[List["Room"]] = relationship(
        "Room",
        back_populates="creator",
        foreign_keys="Room.created_by",
    )
    room_memberships: Mapped[List["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    messages_sent: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="sender",
        foreign_keys="Message.sender_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
