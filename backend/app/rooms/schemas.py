"""
LinguaChat — Rooms Schemas (Pydantic)

Implementation: Yousef Khairy — TASK: Room Management
See: docs/api-contract.md § 3, 4, 5, 6
"""

from pydantic import BaseModel, Field
from typing import List


class CreateRoomRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class RoomResponse(BaseModel):
    id: str
    name: str
    invitation_link: str
    created_by: str
    created_at: str


class RoomListItem(BaseModel):
    id: str
    name: str
    member_count: int
    created_at: str


class RoomListResponse(BaseModel):
    rooms: List[RoomListItem]
    total: int
    limit: int
    offset: int


class JoinRoomResponse(BaseModel):
    room_id: str
    user_id: str
    joined_at: str


class MessageResponse(BaseModel):
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
    messages: List[MessageResponse]
    has_more: bool
