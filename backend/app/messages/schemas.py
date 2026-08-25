from __future__ import annotations
"""
LinguaChat — Messages Schemas (Pydantic)

Shared message data models used across WebSocket and REST endpoints.
Implementation: Yousef Khairy — TASK-05-YOUSEF
See: docs/api-contract.md § 6 & docs/database-schema.md § 4, 5
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageResponse(BaseModel):
    """Single message in room message history (Contract: docs/api-contract.md § 6)."""
    id: str
    room_id: str
    sender_id: str
    sender_username: str
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    sent_at: str

    model_config = ConfigDict(from_attributes=True)


class MessageHistoryResponse(BaseModel):
    """GET /rooms/{room_id}/messages response envelope."""
    messages: List[MessageResponse]
    has_more: bool


class MessageOut(BaseModel):
    """Outbound message shape used across WebSocket broadcast and REST history."""
    id: str
    room_id: str
    sender_id: str
    sender_username: str
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    translation_source: Optional[str] = "original"
    sent_at: str
