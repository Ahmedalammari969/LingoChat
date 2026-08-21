"""
LinguaChat — Rooms Router (Skeleton)

Endpoints: POST /rooms, GET /rooms, POST /rooms/{room_id}/join, GET /rooms/{room_id}/messages
Implementation: Yousef Khairy — TASK: Room Management
See: docs/api-contract.md § 3, 4, 5, 6
"""

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.rooms import service as rooms_service
from app.rooms.schemas import (
    CreateRoomRequest, RoomResponse, RoomListResponse,
    JoinRoomResponse, MessageHistoryResponse
)

router = APIRouter()


@router.post("", response_model=RoomResponse, status_code=201)
async def create_room(
    data: CreateRoomRequest,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user),  # add when auth is implemented
) -> RoomResponse:
    """Create a new chat room. Contract: docs/api-contract.md § 3."""
    raise NotImplementedError("Awaiting auth implementation — Yousef Khairy")


@router.get("", response_model=RoomListResponse)
async def list_rooms(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> RoomListResponse:
    """List rooms. Contract: docs/api-contract.md § 4."""
    return await rooms_service.list_rooms(db, limit, offset)


@router.post("/{room_id}/join", response_model=JoinRoomResponse)
async def join_room(
    room_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JoinRoomResponse:
    """Join a room. Contract: docs/api-contract.md § 5."""
    raise NotImplementedError("Awaiting auth implementation — Yousef Khairy")


@router.get("/{room_id}/messages", response_model=MessageHistoryResponse)
async def get_messages(
    room_id: uuid.UUID,
    limit: int = Query(default=50, le=200),
    before: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> MessageHistoryResponse:
    """Message history. Contract: docs/api-contract.md § 6."""
    raise NotImplementedError("Awaiting auth implementation — Yousef Khairy")
