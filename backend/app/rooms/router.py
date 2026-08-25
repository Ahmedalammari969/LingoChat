from __future__ import annotations
"""
LinguaChat — Rooms Router

Endpoints:
- POST /rooms — Create a room
- GET /rooms — List rooms
- POST /rooms/{room_id}/join — Join a room
Implementation: Yousef Khairy — TASK-04-YOUSEF
See: docs/api-contract.md § 3, 4, 5
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.database.models.user import User
from app.database.session import get_db
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
