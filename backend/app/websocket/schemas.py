from __future__ import annotations
"""
LinguaChat — WebSocket Schemas (Pydantic)

Pydantic models for WebSocket message validation.
Implementation: Mohammed Al-Daees — TASK-01-MOHAMMED
Contract: docs/websocket-contract.md § Base Message Format & Message Types
"""

from enum import Enum
from typing import Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# ── Official WebSocket Message Types ──────────────────────────────────────────
# Defined strictly in docs/websocket-contract.md § Message Types
# NO new types may be added without Team Leader approval.

class WSMessageType(str, Enum):
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    TEXT_MESSAGE = "TEXT_MESSAGE"
    TYPING = "TYPING"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


# ── Official Error Codes ───────────────────────────────────────────────────────
# Defined in docs/websocket-contract.md § ERROR

class WSErrorCode(str, Enum):
    INVALID_JSON = "INVALID_JSON"
    UNKNOWN_MESSAGE_TYPE = "UNKNOWN_MESSAGE_TYPE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    EMPTY_MESSAGE = "EMPTY_MESSAGE"
    TRANSLATION_FAILED = "TRANSLATION_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"
    NOT_ROOM_MEMBER = "NOT_ROOM_MEMBER"
    SERVER_ERROR = "SERVER_ERROR"


# ── Base Envelope ─────────────────────────────────────────────────────────────

class WSMessageEnvelope(BaseModel):
    """
    Standard envelope format for all WebSocket messages.
    See docs/websocket-contract.md § Base Message Format
    """
    type: WSMessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    room_id: str


# ── Payload Models for Specific Message Types ─────────────────────────────────

class JoinPayload(BaseModel):
    """Server -> All Clients when a user joins."""
    user_id: str
    username: str = Field(..., max_length=50)


class LeavePayload(BaseModel):
    """Server -> Remaining Clients when a user leaves/disconnects."""
    user_id: str
    username: str = Field(..., max_length=50)


class TextMessageOutboundPayload(BaseModel):
    """Client -> Server: Sending a text message."""
    text: str = Field(..., min_length=1, max_length=4096)
    original_language: Optional[str] = None


class TextMessageInboundPayload(BaseModel):
    """Server -> Client: Delivering translated text message."""
    message_id: str
    sender_id: str
    sender_username: str = Field(..., max_length=50)
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    translation_source: str = Field(
        ...,
        description="One of: libretranslate | google | cache | identity"
    )


class TypingOutboundPayload(BaseModel):
    """Client -> Server: Typing status notification."""
    is_typing: bool


class TypingInboundPayload(BaseModel):
    """Server -> Other Clients: Broadcast typing status."""
    user_id: str
    username: str = Field(..., max_length=50)
    is_typing: bool


class HeartbeatPayload(BaseModel):
    """Client -> Server: Ping keep-alive payload."""
    pass


class ErrorPayload(BaseModel):
    """Server -> Client: Specific error notification."""
    code: str
    message: str
    original_type: Optional[str] = None
