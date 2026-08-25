from __future__ import annotations
"""
LinguaChat — Messages Database Service

Handles message persistence, translation storage, and multilingual history retrieval.
Implementation: Yousef Khairy — TASK-05-YOUSEF
See: docs/database-schema.md § 4, 5 & docs/api-contract.md § 6
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
import uuid

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.database.models.message import Message
from app.database.models.translation import Translation
from app.database.models.user import User
from app.messages.schemas import MessageHistoryResponse, MessageResponse


def _to_uuid(val: Union[uuid.UUID, str]) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except ValueError:
        raise ValidationError(f"Invalid UUID format: {val}")


async def save_message(
    db: AsyncSession,
    room_id: Union[uuid.UUID, str],
    sender_id: Optional[Union[uuid.UUID, str]],
    original_text: str,
    original_language: str,
) -> Message:
    """
    Persist a new message into the database.

    Args:
        db: Async database session.
        room_id: UUID of the room.
        sender_id: UUID of the sender (or None for system).
        original_text: Raw message content.
        original_language: Language code of original message (e.g., 'ar', 'en').

    Returns:
        Persisted Message ORM instance.
    """
    r_uuid = _to_uuid(room_id)
    s_uuid = _to_uuid(sender_id) if sender_id else None

    clean_text = original_text.strip()
    if not clean_text:
        raise ValidationError("Message text cannot be empty")

    msg = Message(
        room_id=r_uuid,
        sender_id=s_uuid,
        original_text=clean_text,
        original_language=original_language.strip().lower(),
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


# Alias for compatibility with team contracts
create_message = save_message


async def save_translation(
    db: AsyncSession,
    message_id: Union[uuid.UUID, str],
    target_language: str,
    translated_text: str,
    provider_used: str,
    confidence: Optional[float] = None,
) -> Translation:
    """
    Persist or update a message translation into the database.

    Args:
        db: Async database session.
        message_id: UUID of original message.
        target_language: Target language code.
        translated_text: Resulting translated string.
        provider_used: Provider identifier (e.g., 'libretranslate', 'mymemory').
        confidence: Translation confidence score.

    Returns:
        Persisted Translation ORM instance.
    """
    m_uuid = _to_uuid(message_id)
    target_lang = target_language.strip().lower()

    # Check for existing translation
    query = select(Translation).where(
        Translation.message_id == m_uuid,
        Translation.target_language == target_lang,
    )
    result = await db.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        existing.translated_text = translated_text
        existing.provider_used = provider_used
        existing.confidence = confidence
        db.add(existing)
        await db.flush()
        await db.refresh(existing)
        return existing

    translation = Translation(
        message_id=m_uuid,
        target_language=target_lang,
        translated_text=translated_text,
        provider_used=provider_used,
        confidence=confidence,
    )
    db.add(translation)
    await db.flush()
    await db.refresh(translation)
    return translation


async def get_room_messages(
    db: AsyncSession,
    room_id: Union[uuid.UUID, str],
    user_lang: str,
    limit: int = 50,
    before: Optional[str] = None,
) -> MessageHistoryResponse:
    """
    Retrieve message history for a room, paired with translations in the user's preferred language.

    Args:
        db: Async database session.
        room_id: UUID of the room.
        user_lang: Preferred language code of the requesting user.
        limit: Max number of messages to return (1-200).
        before: Optional ISO timestamp cursor for pagination.

    Returns:
        MessageHistoryResponse with list of messages and has_more flag.
    """
    r_uuid = _to_uuid(room_id)
    target_lang = user_lang.strip().lower() if user_lang else "en"
    clamped_limit = max(1, min(limit, 200))

    query = (
        select(
            Message,
            User.username.label("sender_username"),
            Translation.translated_text.label("translated_text"),
            Translation.target_language.label("target_language"),
        )
        .outerjoin(User, Message.sender_id == User.id)
        .outerjoin(
            Translation,
            and_(
                Message.id == Translation.message_id,
                Translation.target_language == target_lang,
            ),
        )
        .where(Message.room_id == r_uuid)
    )

    if before:
        try:
            # Handle ISO8601 timestamps
            clean_before = before.replace("Z", "+00:00")
            before_dt = datetime.fromisoformat(clean_before)
            query = query.where(Message.sent_at < before_dt)
        except Exception:
            # If invalid timestamp format, ignore before filter
            pass

    # Order by newest first, fetch limit + 1 to calculate has_more
    query = query.order_by(Message.sent_at.desc()).limit(clamped_limit + 1)
    result = await db.execute(query)
    rows = result.all()

    has_more = len(rows) > clamped_limit
    active_rows = rows[:clamped_limit]

    message_items: List[MessageResponse] = []
    for row in active_rows:
        msg: Message = row[0]
        sender_username = row.sender_username or "Unknown"

        # Determine translated text
        if row.translated_text is not None:
            final_translated = row.translated_text
            final_target_lang = row.target_language or target_lang
        elif msg.original_language == target_lang:
            # If original language is already user's language
            final_translated = msg.original_text
            final_target_lang = target_lang
        else:
            # Fallback to original text if no translation is stored yet
            final_translated = msg.original_text
            final_target_lang = target_lang

        message_items.append(
            MessageResponse(
                id=str(msg.id),
                room_id=str(msg.room_id),
                sender_id=str(msg.sender_id) if msg.sender_id else "",
                sender_username=sender_username,
                original_text=msg.original_text,
                original_language=msg.original_language,
                translated_text=final_translated,
                target_language=final_target_lang,
                sent_at=msg.sent_at.isoformat(),
            )
        )

    # Return chronological order (oldest first)
    message_items.reverse()

    return MessageHistoryResponse(
        messages=message_items,
        has_more=has_more,
    )
