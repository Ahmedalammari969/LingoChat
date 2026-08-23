"""
LinguaChat — WebSocket Package
"""

from app.websocket.schemas import (
    WSMessageType,
    WSErrorCode,
    WSMessageEnvelope,
    JoinPayload,
    LeavePayload,
    TextMessageOutboundPayload,
    TextMessageInboundPayload,
    TypingOutboundPayload,
    TypingInboundPayload,
    HeartbeatPayload,
    ErrorPayload,
)
from app.websocket.protocol import (
    WSMessage,
    WSProtocolError,
    parse_message,
    parse_and_validate_message,
    create_error_message,
    build_error_message,
    MAX_MESSAGE_BYTES,
)
from app.websocket.manager import ConnectionManager, manager
from app.websocket.router import router

__all__ = [
    "router",
    "manager",
    "ConnectionManager",
    "WSMessageType",
    "WSErrorCode",
    "WSMessageEnvelope",
    "JoinPayload",
    "LeavePayload",
    "TextMessageOutboundPayload",
    "TextMessageInboundPayload",
    "TypingOutboundPayload",
    "TypingInboundPayload",
    "HeartbeatPayload",
    "ErrorPayload",
    "WSMessage",
    "WSProtocolError",
    "parse_message",
    "parse_and_validate_message",
    "create_error_message",
    "build_error_message",
    "MAX_MESSAGE_BYTES",
]
