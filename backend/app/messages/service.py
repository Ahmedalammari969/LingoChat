from __future__ import annotations
"""
LinguaChat — Messages Service (Skeleton)

Handles message persistence and retrieval.
Implementation: Yousef Khairy — TASK: Database / Messages
See: docs/database-schema.md, docs/api-contract.md
"""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


async def save_message(
    db: AsyncSession,
    room_id: uuid.UUID,
    sender_id: uuid.UUID,
    original_text: str,
    original_language: str,
) -> dict:
    """
    Persist a message to the database.

    Returns:
        Dict with message_id and sent_at.

    Implementation: Yousef Khairy
    """
    raise NotImplementedError("Implement in database task — Yousef Khairy")


async def save_translation(
    db: AsyncSession,
    message_id: uuid.UUID,
    target_language: str,
    translated_text: str,
    provider_used: str,
    confidence: Optional[float] = None,
) -> None:
    """
    Persist a translation result for a message.
    Uses INSERT OR IGNORE pattern (on conflict do nothing).

    Implementation: Yousef Khairy
    """
    raise NotImplementedError("Implement in database task — Yousef Khairy")
