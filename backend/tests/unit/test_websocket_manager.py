"""
LinguaChat — WebSocket ConnectionManager Unit Tests
Tests for TASK-02-MOHAMMED
Contract: docs/websocket-contract.md § Connection Lifecycle & Heartbeat
"""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.websocket.manager import ConnectionManager


class MockWebSocket:
    """Mock WebSocket for unit testing."""

    def __init__(self, should_fail: bool = False):
        self.accepted = False
        self.sent_messages = []
        self.should_fail = should_fail

    async def accept(self):
        self.accepted = True

    async def send_text(self, text: str):
        if self.should_fail:
            raise RuntimeError("Broken connection pipe")
        self.sent_messages.append(text)


@pytest.mark.asyncio
async def test_connection_lifecycle_and_counts():
    """Test connecting, checking active counts, and disconnecting."""
    mgr = ConnectionManager()
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    ws3 = MockWebSocket()

    # Connect to room 1
    await mgr.connect(ws1, room_id="room-1", user_id="user-1", username="ahmed", preferred_language="ar")
    await mgr.connect(ws2, room_id="room-1", user_id="user-2", username="mohammed", preferred_language="en")

    # Connect to room 2
    await mgr.connect(ws3, room_id="room-2", user_id="user-3", username="yousef", preferred_language="fr")

    assert ws1.accepted is True
    assert ws2.accepted is True
    assert ws3.accepted is True

    assert mgr.get_room_user_count("room-1") == 2
    assert mgr.get_room_user_count("room-2") == 1
    assert mgr.get_room_user_count("room-empty") == 0
    assert mgr.get_active_connections_count() == 3

    assert mgr.is_user_in_room("room-1", "user-1") is True
    assert mgr.is_user_in_room("room-1", "user-3") is False

    members = mgr.get_room_members("room-1")
    assert len(members) == 2
    usernames = {m["username"] for m in members}
    assert "ahmed" in usernames
    assert "mohammed" in usernames

    # Disconnect user 1
    await mgr.disconnect(ws1, room_id="room-1", user_id="user-1")
    assert mgr.get_room_user_count("room-1") == 1
    assert mgr.get_active_connections_count() == 2

    # Disconnect user 2 -> room 1 becomes empty and pruned
    await mgr.disconnect(ws2, room_id="room-1", user_id="user-2")
    assert mgr.get_room_user_count("room-1") == 0
    assert mgr.get_active_connections_count() == 1


@pytest.mark.asyncio
async def test_room_isolation_and_broadcast():
    """Test that broadcast to Room A never leaks to Room B."""
    mgr = ConnectionManager()
    ws_room1_user1 = MockWebSocket()
    ws_room1_user2 = MockWebSocket()
    ws_room2_user3 = MockWebSocket()

    await mgr.connect(ws_room1_user1, room_id="room-A", user_id="u1", username="User 1")
    await mgr.connect(ws_room1_user2, room_id="room-A", user_id="u2", username="User 2")
    await mgr.connect(ws_room2_user3, room_id="room-B", user_id="u3", username="User 3")

    # Broadcast message to Room A
    msg = {"type": "TEXT_MESSAGE", "payload": {"text": "Secret for Room A"}, "room_id": "room-A"}
    delivered = await mgr.broadcast_to_room("room-A", msg)

    assert delivered == 2
    assert len(ws_room1_user1.sent_messages) == 1
    assert len(ws_room1_user2.sent_messages) == 1
    # Room B must receive NOTHING
    assert len(ws_room2_user3.sent_messages) == 0


@pytest.mark.asyncio
async def test_broadcast_with_exclusion():
    """Test broadcast excluding the sender."""
    mgr = ConnectionManager()
    ws1 = MockWebSocket()
    ws2 = MockWebSocket()

    await mgr.connect(ws1, room_id="room-1", user_id="sender", username="Sender")
    await mgr.connect(ws2, room_id="room-1", user_id="receiver", username="Receiver")

    msg = {"type": "TEXT_MESSAGE", "payload": {"text": "Hello"}, "room_id": "room-1"}
    delivered = await mgr.broadcast_to_room("room-1", msg, exclude_user_id="sender")

    assert delivered == 1
    assert len(ws1.sent_messages) == 0  # Excluded
    assert len(ws2.sent_messages) == 1  # Delivered


@pytest.mark.asyncio
async def test_custom_broadcast_per_language():
    """Test broadcasting tailored messages per recipient's language preference."""
    mgr = ConnectionManager()
    ws_ar = MockWebSocket()
    ws_en = MockWebSocket()

    await mgr.connect(ws_ar, room_id="room-chat", user_id="u-ar", username="Ali", preferred_language="ar")
    await mgr.connect(ws_en, room_id="room-chat", user_id="u-en", username="John", preferred_language="en")

    def language_factory(conn_info):
        lang = conn_info["preferred_language"]
        if lang == "ar":
            return {"type": "TEXT_MESSAGE", "payload": {"text": "مرحبا"}}
        return {"type": "TEXT_MESSAGE", "payload": {"text": "Hello"}}

    delivered = await mgr.broadcast_custom("room-chat", language_factory)
    assert delivered == 2

    assert json.loads(ws_ar.sent_messages[0])["payload"]["text"] == "مرحبا"
    assert json.loads(ws_en.sent_messages[0])["payload"]["text"] == "Hello"


@pytest.mark.asyncio
async def test_send_personal_message():
    """Test sending a direct private message to a specific connection."""
    mgr = ConnectionManager()
    ws = MockWebSocket()
    await mgr.connect(ws, room_id="room-1", user_id="u1", username="User")

    success = await mgr.send_personal_message({"type": "HEARTBEAT", "payload": {}}, ws)
    assert success is True
    assert len(ws.sent_messages) == 1


@pytest.mark.asyncio
async def test_record_heartbeat():
    """Test recording heartbeat pings."""
    mgr = ConnectionManager()
    ws = MockWebSocket()
    await mgr.connect(ws, room_id="room-1", user_id="u1", username="User")

    assert mgr.record_heartbeat("room-1", "u1") is True
    assert mgr.record_heartbeat("room-1", "non-existent") is False
    assert mgr.record_heartbeat("non-existent-room", "u1") is False


@pytest.mark.asyncio
async def test_resilience_to_broken_connections():
    """Test that a failing connection does not break broadcasts to other members and gets cleaned up."""
    mgr = ConnectionManager()
    ws_healthy = MockWebSocket(should_fail=False)
    ws_broken = MockWebSocket(should_fail=True)

    await mgr.connect(ws_healthy, room_id="room-test", user_id="healthy-user", username="Healthy")
    await mgr.connect(ws_broken, room_id="room-test", user_id="broken-user", username="Broken")

    assert mgr.get_room_user_count("room-test") == 2

    delivered = await mgr.broadcast_to_room("room-test", {"type": "HEARTBEAT"})
    assert delivered == 1
    assert len(ws_healthy.sent_messages) == 1

    # The broken connection should have been automatically cleaned up
    assert mgr.get_room_user_count("room-test") == 1
    assert mgr.is_user_in_room("room-test", "broken-user") is False
