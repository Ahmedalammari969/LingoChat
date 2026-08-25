from __future__ import annotations
"""
LinguaChat — Rooms Schemas (Pydantic)

Request and response schemas for room management endpoints.
Implementation: Yousef Khairy — TASK-04-YOUSEF
See: docs/api-contract.md § 3, 4, 5, 6
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateRoomRequest(BaseModel):
    """POST /rooms request body."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Display name of the chat room (1-100 characters)",
    )


class RoomResponse(BaseModel):
    """POST /rooms success response (201 Created)."""
    id: str
    name: str
    invitation_link: str
    created_by: str
    created_at: str


class RoomListItem(BaseModel):
    """Single room item in room list."""
    id: str
    name: str
    member_count: int
    created_at: str


class RoomListResponse(BaseModel):
    """GET /rooms success response (200 OK)."""
    rooms: List[RoomListItem]
    total: int
    limit: int
    offset: int


class JoinRoomResponse(BaseModel):
    """POST /rooms/{room_id}/join success response (200 OK)."""
    room_id: str
    user_id: str
    joined_at: str


class MessageResponse(BaseModel):
    """Single message in room message history."""
    id: str
    room_id: str
    sender_id: str
    sender_username: str
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    sent_at: str


class MessageHistoryResponse(BaseModel):
    """GET /rooms/{room_id}/messages success response (200 OK)."""
    messages: List[MessageResponse]
    has_more: bool
