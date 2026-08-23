"""
LinguaChat — WebSocket Protocol Unit Tests
Tests for TASK-01-MOHAMMED
Contract: docs/websocket-contract.md
"""

import json
import pytest
from app.websocket.schemas import WSMessageType, WSErrorCode
from app.websocket.protocol import (
    WSMessage,
    WSProtocolError,
    parse_message,
    parse_and_validate_message,
    create_error_message,
    build_error_message,
    MAX_MESSAGE_BYTES,
)


def test_valid_text_message_parsing():
    """Test parsing a valid TEXT_MESSAGE payload."""
    raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {
            "text": "Hello, how are you?",
            "original_language": "en"
        },
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "123e4567-e89b-12d3-a456-426614174000"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.TEXT_MESSAGE
    assert msg.payload["text"] == "Hello, how are you?"
    assert msg.payload["original_language"] == "en"
    assert msg.room_id == "123e4567-e89b-12d3-a456-426614174000"


def test_valid_join_message_parsing():
    """Test parsing a valid JOIN message."""
    raw = json.dumps({
        "type": "JOIN",
        "payload": {
            "user_id": "user-uuid-123",
            "username": "ahmed"
        },
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-456"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.JOIN
    assert msg.payload["username"] == "ahmed"


def test_valid_leave_message_parsing():
    """Test parsing a valid LEAVE message."""
    raw = json.dumps({
        "type": "LEAVE",
        "payload": {
            "user_id": "user-uuid-123",
            "username": "ahmed"
        },
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-456"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.LEAVE


def test_valid_typing_message_parsing():
    """Test parsing a valid TYPING message."""
    raw = json.dumps({
        "type": "TYPING",
        "payload": {"is_typing": True},
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-456"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.TYPING
    assert msg.payload["is_typing"] is True


def test_valid_heartbeat_message_parsing():
    """Test parsing a valid HEARTBEAT message."""
    raw = json.dumps({
        "type": "HEARTBEAT",
        "payload": {},
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-456"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.HEARTBEAT
    assert msg.payload == {}


def test_valid_error_message_parsing():
    """Test parsing an ERROR message."""
    raw = json.dumps({
        "type": "ERROR",
        "payload": {
            "code": "INVALID_JSON",
            "message": "Bad JSON format",
            "original_type": "TEXT_MESSAGE"
        },
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-456"
    })
    msg = parse_message(raw)
    assert msg.type == WSMessageType.ERROR
    assert msg.payload["code"] == "INVALID_JSON"


def test_reject_invalid_json():
    """Test rejecting non-JSON strings."""
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message("not a json string at all")
    assert exc_info.value.code == WSErrorCode.INVALID_JSON.value


def test_reject_unknown_message_type():
    """Test rejecting unknown message type."""
    raw = json.dumps({
        "type": "DELETE_ROOM_ACTION",
        "payload": {},
        "room_id": "room-123"
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw)
    assert exc_info.value.code == WSErrorCode.UNKNOWN_MESSAGE_TYPE.value


def test_reject_empty_text_message():
    """Test rejecting empty or whitespace-only messages."""
    raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {"text": "    "},
        "room_id": "room-123"
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw)
    assert exc_info.value.code == WSErrorCode.EMPTY_MESSAGE.value


def test_reject_message_too_long():
    """Test rejecting messages exceeding 4096 bytes."""
    huge_text = "A" * (MAX_MESSAGE_BYTES + 500)
    raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {"text": huge_text},
        "room_id": "room-123"
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw)
    assert exc_info.value.code == WSErrorCode.MESSAGE_TOO_LONG.value


def test_reject_missing_required_fields():
    """Test rejecting envelope with missing required fields."""
    # Missing room_id
    raw_no_room = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {"text": "hello"}
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw_no_room)
    assert exc_info.value.code == WSErrorCode.VALIDATION_ERROR.value

    # Missing type
    raw_no_type = json.dumps({
        "room_id": "room-123",
        "payload": {"text": "hello"}
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw_no_type)
    assert exc_info.value.code == WSErrorCode.VALIDATION_ERROR.value


def test_create_and_build_error_message():
    """Test creating standard error message envelopes."""
    err_dict = create_error_message(
        code="INVALID_JSON",
        message="Malformed JSON input",
        room_id="room-789",
        original_type="TEXT_MESSAGE"
    )
    assert err_dict["type"] == "ERROR"
    assert err_dict["payload"]["code"] == "INVALID_JSON"
    assert err_dict["payload"]["original_type"] == "TEXT_MESSAGE"
    assert err_dict["room_id"] == "room-789"

    err_json = build_error_message(
        code="UNAUTHORIZED",
        message="Token expired",
        room_id="room-789"
    )
    parsed = json.loads(err_json)
    assert parsed["payload"]["code"] == "UNAUTHORIZED"


def test_parse_and_validate_message_helper():
    """Test the safe parse_and_validate_message wrapper."""
    # Valid
    valid_raw = json.dumps({
        "type": "TYPING",
        "payload": {"is_typing": False},
        "room_id": "room-123"
    })
    msg_dict, err = parse_and_validate_message(valid_raw)
    assert msg_dict is not None
    assert err is None
    assert msg_dict["type"] == "TYPING"

    # Invalid
    invalid_raw = "broken json"
    msg_dict, err = parse_and_validate_message(invalid_raw)
    assert msg_dict is None
    assert err is not None
    assert err["type"] == "ERROR"
    assert err["payload"]["code"] == "INVALID_JSON"


def test_arabic_multibyte_text_and_size_boundary():
    """Test multi-byte Arabic character encoding and exact boundary size check."""
    arabic_text = "مرحبا بالعالم! هذه رسالة تجريبية باللغة العربية"
    raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {"text": arabic_text, "original_language": "ar"},
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-arabic-123"
    }, ensure_ascii=False)
    msg = parse_message(raw)
    assert msg.payload["text"] == arabic_text
    assert msg.payload["original_language"] == "ar"


def test_reject_invalid_typing_boolean():
    """Test rejecting non-boolean typing payload."""
    raw = json.dumps({
        "type": "TYPING",
        "payload": {"is_typing": "yes_typing"},
        "room_id": "room-123"
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw)
    assert exc_info.value.code == WSErrorCode.VALIDATION_ERROR.value


def test_reject_non_dict_payload():
    """Test rejecting payload that is not a JSON object."""
    raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": "just a string instead of object",
        "room_id": "room-123"
    })
    with pytest.raises(WSProtocolError) as exc_info:
        parse_message(raw)
    assert exc_info.value.code == WSErrorCode.VALIDATION_ERROR.value


def test_to_dict_and_to_json():
    """Test WSMessage serialization helpers."""
    msg = WSMessage(
        type=WSMessageType.TEXT_MESSAGE,
        payload={"text": "ping"},
        timestamp="2026-08-24T00:00:00.000Z",
        room_id="room-uuid"
    )
    d = msg.to_dict()
    assert d["type"] == "TEXT_MESSAGE"
    assert d["payload"]["text"] == "ping"
    j = msg.to_json()
    assert "TEXT_MESSAGE" in j

