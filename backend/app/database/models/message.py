from __future__ import annotations
"""
LinguaChat — Message ORM Model

Schema defined in: docs/database-schema.md § 4. messages
Implementation: Yousef Khairy — TASK: Database
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Message(Base):
    """
    Represents a chat message sent within a room.

    - original_text: always stored as sent (no modification)
    - original_language: auto-detected or declared by sender
    - Translations are stored separately in the translations table
    """

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    original_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    original_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    # room = relationship("Room", back_populates="messages")
    # sender = relationship("User", back_populates="messages_sent")
    # translations = relationship("Translation", back_populates="message")

    def __repr__(self) -> str:
        return f"<Message id={self.id} room={self.room_id} lang={self.original_language!r}>"
