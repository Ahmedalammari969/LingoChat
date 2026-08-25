from __future__ import annotations
"""
LinguaChat — Room ORM Model

Schema defined in: docs/database-schema.md § 2. rooms
Implementation: Yousef Khairy — TASK-01-YOUSEF
"""

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, utcnow

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.room_member import RoomMember
    from app.database.models.message import Message


class Room(Base):
    """
    Represents a LinguaChat chat room.
    Each room has a unique ID that serves as the invitation code.
    """

    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    is_private: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    creator: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="rooms_created",
        foreign_keys=[created_by],
    )
    members: Mapped[List["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Room id={self.id} name={self.name!r}>"
