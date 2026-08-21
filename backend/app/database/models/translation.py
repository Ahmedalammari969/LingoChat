from __future__ import annotations
"""
LinguaChat — Translation ORM Model

Schema defined in: docs/database-schema.md § 5. translations
Implementation: Yousef Khairy (schema) / Moayad Al-Soufi (service usage)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Translation(Base):
    """
    Cached translation of a message into a specific target language.

    Unique constraint on (message_id, target_language) ensures
    one translation per language per message.
    """

    __tablename__ = "translations"
    __table_args__ = (
        UniqueConstraint(
            "message_id",
            "target_language",
            name="uq_translations_message_lang",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    translated_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    provider_used: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        # Values: "libretranslate", "google", "cache"
        # See docs/translation-contract.md
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        # 0.0–1.0 or None if provider does not return confidence
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    # message = relationship("Message", back_populates="translations")

    def __repr__(self) -> str:
        return (
            f"<Translation msg={self.message_id} "
            f"lang={self.target_language!r} "
            f"provider={self.provider_used!r}>"
        )
