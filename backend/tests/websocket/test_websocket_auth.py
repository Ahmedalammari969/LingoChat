"""
LinguaChat — WebSocket Authentication & Routing Tests
Tests for TASK-03-MOHAMMED
Contract: docs/websocket-contract.md § Connection Lifecycle & Close Codes
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from jose import jwt

from app.main import app
from app.core.config import settings
from app.websocket.router import set_room_validator, set_membership_validator
from app.websocket.schemas import WSMessageType


def generate_test_jwt(user_id: str, username: str = "testuser", preferred_language: str = "en", expired: bool = False) -> str:
    """Generate a test JWT token."""
    expire = datetime.now(timezone.utc) + (timedelta(minutes=-10) if expired else timedelta(minutes=60))
    payload = {
        "sub": user_id,
        "username": username,
        "preferred_language": preferred_language,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture(autouse=True)
def reset_validators():
    """Reset validators after each test."""
    set_room_validator(None)
    set_membership_validator(None)
    yield
    set_room_validator(None)
    set_membership_validator(None)


def test_reject_missing_token():
    """Test connecting without token closes with code 4001."""
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/room-123"):
            pass
    assert exc_info.value.code == 4001


def test_reject_invalid_token():
    """Test connecting with invalid/tampered token closes with code 4001."""
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/room-123?token=invalid.tampered.token"):
            pass
    assert exc_info.value.code == 4001


def test_reject_expired_token():
    """Test connecting with expired token closes with code 4001."""
    token = generate_test_jwt(user_id="user-123", expired=True)
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/room-123?token={token}"):
            pass
    assert exc_info.value.code == 4001


def test_reject_room_not_found():
    """Test connecting to non-existent room closes with code 4004."""
    # Room validator returns False
    set_room_validator(lambda r_id: False)

    token = generate_test_jwt(user_id="user-123")
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/non-existent-room?token={token}"):
            pass
    assert exc_info.value.code == 4004


def test_reject_non_member():
    """Test connecting when user is not a room member closes with code 4003."""
    set_room_validator(lambda r_id: True)
    set_membership_validator(lambda r_id, u_id: False)

    token = generate_test_jwt(user_id="user-123")
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect(f"/ws/room-123?token={token}"):
            pass
    assert exc_info.value.code == 4003


def test_successful_connection_and_join_broadcast():
    """Test successful connection receives JOIN event and handles messages."""
    set_room_validator(lambda r_id: True)
    set_membership_validator(lambda r_id, u_id: True)

    token = generate_test_jwt(user_id="u-valid-1", username="ahmed", preferred_language="ar")
    client = TestClient(app)

    with client.websocket_connect(f"/ws/room-success-123?token={token}") as websocket:
        # First message broadcasted on join should be the JOIN event
        data = websocket.receive_text()
        msg = json.loads(data)
        assert msg["type"] == WSMessageType.JOIN.value
        assert msg["payload"]["user_id"] == "u-valid-1"
        assert msg["payload"]["username"] == "ahmed"
        assert msg["room_id"] == "room-success-123"

        # Send a HEARTBEAT
        websocket.send_text(json.dumps({
            "type": "HEARTBEAT",
            "payload": {},
            "room_id": "room-success-123"
        }))


def test_typing_indicator_handling():
    """Test sending typing indicator."""
    set_room_validator(lambda r_id: True)
    set_membership_validator(lambda r_id, u_id: True)

    token1 = generate_test_jwt(user_id="user-sender", username="Sender")
    client = TestClient(app)

    with client.websocket_connect(f"/ws/room-typing-123?token={token1}") as ws:
        # Consume JOIN
        join_msg = ws.receive_text()
        assert "JOIN" in join_msg

        # Send TYPING
        ws.send_text(json.dumps({
            "type": "TYPING",
            "payload": {"is_typing": True},
            "room_id": "room-typing-123"
        }))
