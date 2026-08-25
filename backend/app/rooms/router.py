from __future__ import annotations
"""
LinguaChat — Rooms Router

Endpoints:
- POST /rooms — Create a room
- GET /rooms — List rooms
- POST /rooms/{room_id}/join — Join a room
- GET /rooms/{room_id}/messages — Message history
Implementation: Yousef Khairy — TASK-04 & TASK-05
See: docs/api-contract.md § 3, 4, 5, 6
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.core.errors import ForbiddenError, NotFoundError
from app.database.models.user import User
from app.database.session import get_db
from app.messages import service as messages_service
from app.messages.schemas import MessageHistoryResponse
from app.rooms import service as rooms_service
from app.rooms.schemas import (
    CreateRoomRequest,
    JoinRoomResponse,
    RoomListResponse,
    RoomResponse,
)

router = APIRouter()


@router.post(
    "",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat room",
)
async def create_room(
    data: CreateRoomRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> RoomResponse:
    """
    Create a new chat room. The authenticated creator automatically becomes a member.
    Contract: docs/api-contract.md § 3. POST /rooms
    """
    return await rooms_service.create_room(db, data, current_user.id)


@router.get(
    "",
    response_model=RoomListResponse,
    status_code=status.HTTP_200_OK,
    summary="List available rooms",
)
async def list_rooms(
    limit: int = Query(default=20, ge=1, le=100, description="Number of rooms to return"),
    offset: int = Query(default=0, ge=0, description="Number of rooms to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> RoomListResponse:
    """
    List available rooms with pagination and member counts.
    Contract: docs/api-contract.md § 4. GET /rooms
    """
    return await rooms_service.list_rooms(db, limit, offset)


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    status_code=status.HTTP_200_OK,
    summary="Get room details by ID",
)
async def get_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> RoomResponse:
    """Retrieve details for a specific room."""
    room = await rooms_service.get_room_by_id(db, room_id)
    if not room:
        raise NotFoundError("ROOM", str(room_id))
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        invitation_link=f"/rooms/{room.id}/join",
        created_by=str(room.created_by),
        created_at=room.created_at.isoformat(),
        is_private=getattr(room, "is_private", False),
    )


@router.post(
    "/{room_id}/join",
    response_model=JoinRoomResponse,
    status_code=status.HTTP_200_OK,
    summary="Join an existing room",
)
async def join_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> JoinRoomResponse:
    """
    Enroll the authenticated user into an existing chat room.
    Contract: docs/api-contract.md § 5. POST /rooms/{room_id}/join
    """
    return await rooms_service.join_room(db, room_id, current_user.id)


@router.get(
    "/{room_id}/messages",
    response_model=MessageHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve paginated room message history",
)
async def get_messages(
    room_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200, description="Max messages to return"),
    before: Optional[str] = Query(default=None, description="ISO timestamp cursor"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> MessageHistoryResponse:
    """
    Retrieve message history for a room, paired with translations in the user's preferred language.
    Contract: docs/api-contract.md § 6. GET /rooms/{room_id}/messages

    Security:
    - 401 Unauthorized if not logged in.
    - 404 Not Found if room does not exist.
    - 403 Forbidden if user is not a member of the room.
    """
    # 1. Verify room exists
    room = await rooms_service.get_room_by_id(db, room_id)
    if not room:
        raise NotFoundError("ROOM", str(room_id))

    # 2. Verify membership
    is_member = await rooms_service.is_user_member_of_room(db, room_id, current_user.id)
    if not is_member:
        raise ForbiddenError("You are not a member of this room")

    # 3. Retrieve messages
    return await messages_service.get_room_messages(
        db,
        room_id=room_id,
        user_lang=current_user.preferred_language,
        limit=limit,
        before=before,
    )
