"""
LinguaChat — Messages Persistence & History Unit Tests
Tests for TASK-05-YOUSEF
Contract: docs/api-contract.md § 6 & docs/database-schema.md § 4, 5
"""

import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database.models.user import User
from app.database.models.room import Room
from app.database.models.message import Message
from app.database.models.translation import Translation
from app.messages.schemas import MessageHistoryResponse, MessageResponse
from app.core.security import create_access_token
from app.messages import service as messages_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    u_id = uuid.uuid4()
    return User(
        id=u_id,
        username="chat_user",
        hashed_password="hashed_password",
        preferred_language="ar",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )


@pytest.fixture
def auth_header(test_user):
    token = create_access_token(
        subject=str(test_user.id),
        extra_claims={"username": test_user.username, "preferred_language": test_user.preferred_language},
    )
    return {"Authorization": f"Bearer {token}"}


def test_get_room_messages_success_member(client, test_user, auth_header):
    """Test member can retrieve room messages with translations (200 OK)."""
    r_id = uuid.uuid4()
    mock_room = Room(id=r_id, name="Test Room", created_by=test_user.id)
    mock_history = MessageHistoryResponse(
        messages=[
            MessageResponse(
                id=str(uuid.uuid4()),
                room_id=str(r_id),
                sender_id=str(test_user.id),
                sender_username="alice",
                original_text="Hello world",
                original_language="en",
                translated_text="مرحبا بالعالم",
                target_language="ar",
                sent_at=datetime.now(timezone.utc).isoformat(),
            )
        ],
        has_more=False,
    )

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room, \
         patch("app.rooms.service.is_user_member_of_room", new_callable=AsyncMock) as mock_is_member, \
         patch("app.messages.service.get_room_messages", new_callable=AsyncMock) as mock_get_msgs:

        mock_get_user.return_value = test_user
        mock_get_room.return_value = mock_room
        mock_is_member.return_value = True
        mock_get_msgs.return_value = mock_history

        response = client.get(f"/api/v1/rooms/{r_id}/messages?limit=50", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 1
        assert data["messages"][0]["translated_text"] == "مرحبا بالعالم"
        assert data["messages"][0]["original_text"] == "Hello world"
        assert data["has_more"] is False


def test_get_room_messages_forbidden_for_non_member(client, test_user, auth_header):
    """Test non-member is rejected with 403 Forbidden when requesting room messages."""
    r_id = uuid.uuid4()
    mock_room = Room(id=r_id, name="Secret Room", created_by=uuid.uuid4())

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room, \
         patch("app.rooms.service.is_user_member_of_room", new_callable=AsyncMock) as mock_is_member:

        mock_get_user.return_value = test_user
        mock_get_room.return_value = mock_room
        mock_is_member.return_value = False  # Not a member

        response = client.get(f"/api/v1/rooms/{r_id}/messages", headers=auth_header)

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"


def test_get_room_messages_nonexistent_room_404(client, test_user, auth_header):
    """Test requesting messages for non-existent room returns 404 ROOM_NOT_FOUND."""
    r_id = uuid.uuid4()

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room:

        mock_get_user.return_value = test_user
        mock_get_room.return_value = None  # Room does not exist

        response = client.get(f"/api/v1/rooms/{r_id}/messages", headers=auth_header)

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "ROOM_NOT_FOUND"


def test_get_room_messages_unauthorized_without_token(client):
    """Test requesting messages without token returns 401 Unauthorized."""
    r_id = uuid.uuid4()
    response = client.get(f"/api/v1/rooms/{r_id}/messages")
    assert response.status_code == 401
