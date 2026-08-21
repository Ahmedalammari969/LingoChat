from __future__ import annotations
"""
LinguaChat — Room ORM Model

Schema defined in: docs/database-schema.md § 2. rooms
Implementation: Yousef Khairy — TASK: Database
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


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
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    # creator = relationship("User", back_populates="rooms_created")
    # members = relationship("RoomMember", back_populates="room")
    # messages = relationship("Message", back_populates="room")

    def __repr__(self) -> str:
        return f"<Room id={self.id} name={self.name!r}>"
