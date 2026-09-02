from __future__ import annotations
"""
LinguaChat — WebSocket Protocol & Validation

Defines message parsing, validation, error builders, and type enforcement.
Implementation: Mohammed Al-Daees — TASK-01-MOHAMMED
Contract: docs/websocket-contract.md § Constraints, Special Cases, & Error Codes
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

from app.core.errors import LinguaChatException
from app.websocket.schemas import (
    WSMessageType,
    WSErrorCode,
    WSMessageEnvelope,
    TextMessageOutboundPayload,
    TypingOutboundPayload,
    ErrorPayload,
)

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
# See docs/websocket-contract.md § Constraints & Validation
# NOTE: Increased from 4096 to 65536 to support WebRTC SDP messages
# (RTC_OFFER/RTC_ANSWER contain full SDP which can be 2000-8000+ bytes)
MAX_MESSAGE_BYTES = 65536


# ── Exceptions ────────────────────────────────────────────────────────────────

class WSProtocolError(LinguaChatException):
    """Raised when a WebSocket message violates the protocol contract."""

    def __init__(self, code: str, message: str, original_type: Optional[str] = None):
        self.code = code
        self.message = message
        self.original_type = original_type
        super().__init__(code=code, message=message, status_code=400)


# ── Data Structure ────────────────────────────────────────────────────────────

class WSMessage:
    """
    Represents a parsed and validated WebSocket message.
    Follows docs/websocket-contract.md § Base Message Format.
    """

    def __init__(
        self,
        type: WSMessageType,
        payload: dict[str, Any],
        timestamp: str,
        room_id: str,
    ):
        self.type = type
        self.payload = payload
        self.timestamp = timestamp
        self.room_id = room_id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "type": self.type.value if isinstance(self.type, WSMessageType) else str(self.type),
            "payload": self.payload,
            "timestamp": self.timestamp,
            "room_id": str(self.room_id),
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ── Error Message Builders ────────────────────────────────────────────────────

def create_error_message(
    code: str,
    message: str,
    room_id: str = "",
    original_type: Optional[str] = None,
) -> dict[str, Any]:
    """
    Build a standard error envelope dictionary to send to a client.
    See: docs/websocket-contract.md § ERROR
    """
    error_payload = {
        "code": code,
        "message": message,
        "original_type": original_type,
    }
    return {
        "type": WSMessageType.ERROR.value,
        "payload": error_payload,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "room_id": str(room_id) if room_id else "",
    }


def build_error_message(
    code: str,
    message: str,
    original_type: Optional[str] = None,
    room_id: str = "",
) -> str:
    """
    Build a serialized JSON ERROR message to send to a client.
    See: docs/websocket-contract.md § ERROR
    """
    envelope = create_error_message(
        code=code,
        message=message,
        room_id=room_id,
        original_type=original_type,
    )
    return json.dumps(envelope, ensure_ascii=False)


# ── Parsing & Validation ──────────────────────────────────────────────────────

def parse_message(raw: str) -> WSMessage:
    """
    Parse and strictly validate a raw WebSocket message string according to the contract.

    Args:
        raw: Raw string received over WebSocket.

    Returns:
        Parsed and validated WSMessage.

    Raises:
        WSProtocolError with appropriate error code on failure.
    """
    if not isinstance(raw, str):
        raise WSProtocolError(
            code=WSErrorCode.INVALID_JSON.value,
            message="Message must be a string",
        )

    # 1. Check maximum message size (4096 bytes UTF-8)
    raw_bytes = raw.encode("utf-8")
    if len(raw_bytes) > MAX_MESSAGE_BYTES:
        raise WSProtocolError(
            code=WSErrorCode.MESSAGE_TOO_LONG.value,
            message=f"Message exceeds maximum allowed size of {MAX_MESSAGE_BYTES} bytes",
        )

    # 2. Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise WSProtocolError(
            code=WSErrorCode.INVALID_JSON.value,
            message="Message is not valid JSON",
        )

    if not isinstance(data, dict):
        raise WSProtocolError(
            code=WSErrorCode.VALIDATION_ERROR.value,
            message="Message must be a JSON object",
        )

    # 3. Check Envelope Required Fields
    if "type" not in data or not data["type"]:
        raise WSProtocolError(
            code=WSErrorCode.VALIDATION_ERROR.value,
            message="Missing required field: type",
        )

    raw_type = data["type"]

    # Validate message type against the 6 approved types
    try:
        msg_type = WSMessageType(raw_type)
    except ValueError:
        raise WSProtocolError(
            code=WSErrorCode.UNKNOWN_MESSAGE_TYPE.value,
            message=f"Unknown message type: {raw_type}",
            original_type=str(raw_type),
        )

    if "room_id" not in data or data["room_id"] is None or str(data["room_id"]).strip() == "":
        raise WSProtocolError(
            code=WSErrorCode.VALIDATION_ERROR.value,
            message="Missing required field: room_id",
            original_type=msg_type.value,
        )

    room_id = str(data["room_id"]).strip()
    timestamp = str(data.get("timestamp") or datetime.now(timezone.utc).isoformat())
    payload = data.get("payload")

    if not isinstance(payload, dict):
        raise WSProtocolError(
            code=WSErrorCode.VALIDATION_ERROR.value,
            message="Field 'payload' must be an object",
            original_type=msg_type.value,
        )

    # 4. Type-specific payload validation
    if msg_type == WSMessageType.TEXT_MESSAGE:
        if "text" not in payload:
            raise WSProtocolError(
                code=WSErrorCode.VALIDATION_ERROR.value,
                message="Missing required payload field: text",
                original_type=msg_type.value,
            )
        text_val = payload["text"]
        if not isinstance(text_val, str) or not text_val.strip():
            raise WSProtocolError(
                code=WSErrorCode.EMPTY_MESSAGE.value,
                message="Message text cannot be empty",
                original_type=msg_type.value,
            )
        if len(text_val.encode("utf-8")) > MAX_MESSAGE_BYTES:
            raise WSProtocolError(
                code=WSErrorCode.MESSAGE_TOO_LONG.value,
                message="Message text payload exceeds maximum allowed size",
                original_type=msg_type.value,
            )

    elif msg_type == WSMessageType.TYPING:
        if "is_typing" not in payload or not isinstance(payload["is_typing"], bool):
            raise WSProtocolError(
                code=WSErrorCode.VALIDATION_ERROR.value,
                message="Field 'is_typing' must be a boolean",
                original_type=msg_type.value,
            )

    return WSMessage(
        type=msg_type,
        payload=payload,
        timestamp=timestamp,
        room_id=room_id,
    )


def parse_and_validate_message(
    raw_data: str,
) -> Tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
    """
    Convenience wrapper that returns (valid_message_dict, None) or (None, error_envelope_dict).

    Args:
        raw_data: Raw string received over WebSocket.

    Returns:
        tuple (message_dict or None, error_dict or None)
    """
    try:
        msg = parse_message(raw_data)
        return msg.to_dict(), None
    except WSProtocolError as e:
        err_envelope = create_error_message(
            code=e.code,
            message=e.message,
            original_type=e.original_type,
        )
        return None, err_envelope
    except Exception as ex:
        logger.exception("Unexpected error in WebSocket protocol parsing")
        err_envelope = create_error_message(
            code=WSErrorCode.SERVER_ERROR.value,
            message="Internal server error parsing message",
        )
        return None, err_envelope
