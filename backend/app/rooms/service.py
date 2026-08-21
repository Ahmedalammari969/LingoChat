from __future__ import annotations
"""
LinguaChat — Rooms Service (Skeleton)

Implementation: Yousef Khairy — TASK: Room Management
See: docs/api-contract.md § 3, 4, 5, 6
"""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.rooms.schemas import (
    CreateRoomRequest, RoomResponse, RoomListResponse,
    JoinRoomResponse, MessageHistoryResponse
)


async def create_room(db: AsyncSession, data: CreateRoomRequest, user_id: uuid.UUID) -> RoomResponse:
    """
    Create a new chat room.
    - Generate invitation_link using room UUID.
    - Creator automatically becomes a member.
    """
    raise NotImplementedError("Implement in room management task — Yousef Khairy")


async def list_rooms(db: AsyncSession, limit: int = 20, offset: int = 0) -> RoomListResponse:
    """List available rooms with member count."""
    raise NotImplementedError("Implement in room management task — Yousef Khairy")


async def join_room(db: AsyncSession, room_id: uuid.UUID, user_id: uuid.UUID) -> JoinRoomResponse:
    """
    Add user to room.
    Raises NotFoundError if room doesn't exist.
    Raises ConflictError("ALREADY_IN_ROOM") if already a member.
    """
    raise NotImplementedError("Implement in room management task — Yousef Khairy")


async def get_room_messages(
    db: AsyncSession,
    room_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 50,
    before: Optional[str] = None,
) -> MessageHistoryResponse:
    """
    Return paginated message history for a room.
    Translated into requesting user's preferred language.
    Raises ForbiddenError if user is not a member.
    """
    raise NotImplementedError("Implement in room management task — Yousef Khairy")


async def is_room_member(db: AsyncSession, room_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Check if a user is a member of a room. Used by WebSocket and message endpoints."""
    raise NotImplementedError("Implement in room management task — Yousef Khairy")
