"""
LinguaChat — Messages Schemas (Pydantic)

Shared message data models used across WebSocket and REST.
"""

from pydantic import BaseModel
from typing import Optional


class MessageOut(BaseModel):
    """Outbound message shape — used in both WebSocket broadcast and REST history."""
    id: str
    room_id: str
    sender_id: str
    sender_username: str
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    translation_source: str
    sent_at: str
