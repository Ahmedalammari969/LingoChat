"""
LinguaChat — WebSocket Protocol (Skeleton)

Defines message parsing, validation, and type enforcement.
Implementation: Mohammed Al-Daees — TASK: WebSocket Gateway
See: docs/websocket-contract.md
"""

from enum import Enum
from typing import Any
import json

from app.core.errors import LinguaChatException


# ── Message Types ─────────────────────────────────────────────────────────────
# Defined in docs/websocket-contract.md
# DO NOT add new types without Team Leader approval.

class WSMessageType(str, Enum):
    JOIN = "JOIN"
    LEAVE = "LEAVE"
    TEXT_MESSAGE = "TEXT_MESSAGE"
    TYPING = "TYPING"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


# ── Constants ─────────────────────────────────────────────────────────────────
MAX_MESSAGE_BYTES = 4096  # See docs/websocket-contract.md § Constraints


class WSMessage:
    """
    Represents a parsed and validated WebSocket message.
    See docs/websocket-contract.md for full format specification.
    """

    def __init__(self, type: WSMessageType, payload: dict, timestamp: str, room_id: str):
        self.type = type
        self.payload = payload
        self.timestamp = timestamp
        self.room_id = room_id


def parse_message(raw: str) -> WSMessage:
    """
    Parse and validate a raw WebSocket message string.

    Args:
        raw: Raw string received over WebSocket.

    Returns:
        Parsed WSMessage.

    Raises:
        WSProtocolError with appropriate code on failure.

    Implementation: Mohammed Al-Daees
    See: docs/websocket-contract.md § Behavior for Special Cases
    """
    raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")


def build_error_message(code: str, message: str, original_type: str = "", room_id: str = "") -> str:
    """
    Build a serialized ERROR message to send to a client.
    See: docs/websocket-contract.md § ERROR
    """
    raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")


class WSProtocolError(LinguaChatException):
    """Raised when a WebSocket message violates the protocol contract."""

    def __init__(self, code: str, message: str):
        super().__init__(code=code, message=message, status_code=400)
