from __future__ import annotations
"""
LinguaChat — WebSocket Schemas (Pydantic)

Pydantic models for WebSocket message validation.
Implementation: Mohammed Al-Daees — TASK: WebSocket Gateway
See: docs/websocket-contract.md
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from app.websocket.protocol import WSMessageType


class WSMessageEnvelope(BaseModel):
    """Base envelope for all WebSocket messages."""
    type: WSMessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str
    room_id: str


class TextMessagePayload(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    original_language: Optional[str] = None


class TypingPayload(BaseModel):
    is_typing: bool
