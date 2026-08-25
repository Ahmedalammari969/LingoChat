from __future__ import annotations
"""
LinguaChat — Dashboard Service

Aggregates high-level system metrics from database models and runtime connection manager.
Implementation: Yousef Khairy — TASK-06-YOUSEF
Contract: docs/api-contract.md § 7. GET /dashboard/stats
"""

from typing import Dict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.message import Message
from app.database.models.room import Room
from app.database.models.translation import Translation
from app.database.models.user import User


async def get_system_stats(
    db: AsyncSession,
    active_connections: int = 0,
) -> Dict[str, int]:
    """
    Query aggregate system statistics from the database.

    Returns:
        {
            "total_users": int,
            "total_rooms": int,
            "total_messages": int,
            "total_translations": int,
            "active_connections": int
        }
    """
    # 1. Total users
    users_query = select(func.count(User.id))
    users_result = await db.execute(users_query)
    total_users = users_result.scalar_one() or 0

    # 2. Total rooms
    rooms_query = select(func.count(Room.id))
    rooms_result = await db.execute(rooms_query)
    total_rooms = rooms_result.scalar_one() or 0

    # 3. Total messages
    messages_query = select(func.count(Message.id))
    messages_result = await db.execute(messages_query)
    total_messages = messages_result.scalar_one() or 0

    # 4. Total translations
    translations_query = select(func.count(Translation.id))
    translations_result = await db.execute(translations_query)
    total_translations = translations_result.scalar_one() or 0

    return {
        "total_users": int(total_users),
        "total_rooms": int(total_rooms),
        "total_messages": int(total_messages),
        "total_translations": int(total_translations),
        "active_connections": int(max(0, active_connections)),
    }
