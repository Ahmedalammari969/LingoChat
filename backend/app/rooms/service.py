from __future__ import annotations
"""
LinguaChat — Rooms Database Service

Implementation: Yousef Khairy — TASK-04-YOUSEF
See: docs/api-contract.md § 3, 4, 5 & docs/database-schema.md § 2, 3
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.database.models.room import Room
from app.database.models.room_member import RoomMember
from app.rooms.schemas import (
    CreateRoomRequest,
    JoinRoomResponse,
    RoomListItem,
    RoomListResponse,
    RoomResponse,
)


def _to_uuid(val: Union[uuid.UUID, str]) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except ValueError:
        raise ValidationError(f"Invalid UUID format: {val}")


async def get_room_by_id(
    db: AsyncSession,
    room_id: Union[uuid.UUID, str],
) -> Optional[Room]:
    """Retrieve a room entity by its UUID."""
    try:
        r_uuid = _to_uuid(room_id)
    except ValidationError:
        return None

    query = select(Room).where(Room.id == r_uuid)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def is_user_member_of_room(
    db: AsyncSession,
    room_id: Union[uuid.UUID, str],
    user_id: Union[uuid.UUID, str],
) -> bool:
    """
    Check if a user is a confirmed member of a room.
    Used for WebSocket authentication and message access authorization.
    """
    try:
        r_uuid = _to_uuid(room_id)
        u_uuid = _to_uuid(user_id)
    except (ValidationError, Exception):
        return False

    query = select(RoomMember.id).where(
        RoomMember.room_id == r_uuid,
        RoomMember.user_id == u_uuid,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


# Alias for backward compatibility
is_room_member = is_user_member_of_room


async def create_room(
    db: AsyncSession,
    data: CreateRoomRequest,
    user_id: Union[uuid.UUID, str],
) -> RoomResponse:
    """
    Create a new chat room and automatically enroll the creator as a member.

    Contract: docs/api-contract.md § 3. POST /rooms
    """
    u_uuid = _to_uuid(user_id)
    clean_name = data.name.strip()
    if not clean_name:
        raise ValidationError("Room name cannot be empty")

    is_priv = bool(getattr(data, "is_private", False))
    room = Room(
        name=clean_name,
        is_private=is_priv,
        created_by=u_uuid,
    )
    db.add(room)
    await db.flush()
    await db.refresh(room)

    # Automatically add creator as first room member
    creator_membership = RoomMember(
        room_id=room.id,
        user_id=u_uuid,
    )
    db.add(creator_membership)
    await db.flush()

    invitation_link = f"/rooms/{room.id}/join"

    return RoomResponse(
        id=str(room.id),
        name=room.name,
        invitation_link=invitation_link,
        created_by=str(room.created_by),
        created_at=room.created_at.isoformat(),
        is_private=room.is_private,
    )


async def list_rooms(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> RoomListResponse:
    """
    List public chat rooms with member count and total pagination count.
    Private rooms (is_private=True) are hidden from the explore list.

    Contract: docs/api-contract.md § 4. GET /rooms
    """
    clamped_limit = max(1, min(limit, 100))
    clamped_offset = max(0, offset)

    # 1. Total public rooms count
    total_query = select(func.count(Room.id)).where(Room.is_private.is_(False))
    total_result = await db.execute(total_query)
    total_count = total_result.scalar_one() or 0

    # 2. Paginated public rooms with member count query (efficient single query)
    query = (
        select(
            Room.id,
            Room.name,
            Room.created_at,
            func.count(RoomMember.id).label("member_count"),
        )
        .outerjoin(RoomMember, Room.id == RoomMember.room_id)
        .where(Room.is_private.is_(False))
        .group_by(Room.id, Room.name, Room.created_at)
        .order_by(Room.created_at.desc())
        .limit(clamped_limit)
        .offset(clamped_offset)
    )

    result = await db.execute(query)
    rows = result.all()

    room_items = [
        RoomListItem(
            id=str(row.id),
            name=row.name,
            member_count=int(row.member_count),
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]

    return RoomListResponse(
        rooms=room_items,
        total=total_count,
        limit=clamped_limit,
        offset=clamped_offset,
    )


async def join_room(
    db: AsyncSession,
    room_id: Union[uuid.UUID, str],
    user_id: Union[uuid.UUID, str],
) -> JoinRoomResponse:
    """
    Enroll a user into a chat room.

    Raises:
        NotFoundError (404): If room does not exist.
        ConflictError (409): If user is already a member of this room.
    """
    r_uuid = _to_uuid(room_id)
    u_uuid = _to_uuid(user_id)

    # 1. Verify room exists
    room = await get_room_by_id(db, r_uuid)
    if not room:
        raise NotFoundError("ROOM", str(r_uuid))

    # 2. Check if user is already a member
    already_member = await is_user_member_of_room(db, r_uuid, u_uuid)
    if already_member:
        raise ConflictError(
            code="ALREADY_IN_ROOM",
            message=f"User '{u_uuid}' is already a member of room '{r_uuid}'",
        )

    # 3. Add membership
    membership = RoomMember(
        room_id=r_uuid,
        user_id=u_uuid,
    )
    db.add(membership)
    await db.flush()
    await db.refresh(membership)

    return JoinRoomResponse(
        room_id=str(membership.room_id),
        user_id=str(membership.user_id),
        joined_at=membership.joined_at.isoformat(),
    )
