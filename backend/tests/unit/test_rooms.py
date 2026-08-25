"""
LinguaChat — Rooms API & Service Unit Tests
Tests for TASK-04-YOUSEF
Contract: docs/api-contract.md § 3, 4, 5
"""

import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database.models.user import User
from app.database.models.room import Room
from app.database.models.room_member import RoomMember
from app.rooms.schemas import (
    CreateRoomRequest,
    RoomResponse,
    RoomListResponse,
    RoomListItem,
    JoinRoomResponse,
)
from app.core.security import create_access_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    u_id = uuid.uuid4()
    return User(
        id=u_id,
        username="room_tester",
        hashed_password="hashed_password",
        preferred_language="ar",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )


@pytest.fixture
def auth_header(test_user):
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


def test_create_room_success(client, test_user, auth_header):
    """Test creating a room returns 201 Created and invitation link."""
    r_id = uuid.uuid4()
    mock_response = RoomResponse(
        id=str(r_id),
        name="Study Group",
        invitation_link=f"/rooms/{r_id}/join",
        created_by=str(test_user.id),
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.create_room", new_callable=AsyncMock) as mock_create_room:

        mock_get_user.return_value = test_user
        mock_create_room.return_value = mock_response

        response = client.post(
            "/api/v1/rooms",
            headers=auth_header,
            json={"name": "Study Group"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Study Group"
        assert data["created_by"] == str(test_user.id)
        assert data["invitation_link"] == f"/rooms/{r_id}/join"
        assert "id" in data
        assert data["is_private"] is False


def test_create_private_room_success(client, test_user, auth_header):
    """Test creating a private room returns 201 Created with is_private=True."""
    r_id = uuid.uuid4()
    mock_response = RoomResponse(
        id=str(r_id),
        name="Secret Study Room",
        invitation_link=f"/rooms/{r_id}/join",
        created_by=str(test_user.id),
        created_at=datetime.now(timezone.utc).isoformat(),
        is_private=True,
    )

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.create_room", new_callable=AsyncMock) as mock_create_room:

        mock_get_user.return_value = test_user
        mock_create_room.return_value = mock_response

        response = client.post(
            "/api/v1/rooms",
            headers=auth_header,
            json={"name": "Secret Study Room", "is_private": True},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Secret Study Room"
        assert data["is_private"] is True


def test_create_room_unauthorized_without_token(client):
    """Test creating a room without auth header returns 401 Unauthorized."""
    response = client.post("/api/v1/rooms", json={"name": "Public Room"})
    assert response.status_code == 401


def test_list_rooms_success(client, test_user, auth_header):
    """Test listing rooms returns 200 OK with member_count and pagination."""
    r_id = uuid.uuid4()
    mock_list_response = RoomListResponse(
        rooms=[
            RoomListItem(
                id=str(r_id),
                name="Main Lobby",
                member_count=5,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        ],
        total=1,
        limit=20,
        offset=0,
    )

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.list_rooms", new_callable=AsyncMock) as mock_list_rooms:

        mock_get_user.return_value = test_user
        mock_list_rooms.return_value = mock_list_response

        response = client.get("/api/v1/rooms?limit=20&offset=0", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert len(data["rooms"]) == 1
        assert data["rooms"][0]["name"] == "Main Lobby"
        assert data["rooms"][0]["member_count"] == 5
        assert data["total"] == 1


def test_join_room_success(client, test_user, auth_header):
    """Test joining an existing room returns 200 OK."""
    r_id = uuid.uuid4()
    mock_join_response = JoinRoomResponse(
        room_id=str(r_id),
        user_id=str(test_user.id),
        joined_at=datetime.now(timezone.utc).isoformat(),
    )

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join_room:

        mock_get_user.return_value = test_user
        mock_join_room.return_value = mock_join_response

        response = client.post(f"/api/v1/rooms/{r_id}/join", headers=auth_header)

        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == str(r_id)
        assert data["user_id"] == str(test_user.id)


def test_join_room_nonexistent_404(client, test_user, auth_header):
    """Test joining a non-existent room returns 404 ROOM_NOT_FOUND."""
    r_id = uuid.uuid4()
    from app.core.errors import NotFoundError

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join_room:

        mock_get_user.return_value = test_user
        mock_join_room.side_effect = NotFoundError("ROOM", str(r_id))

        response = client.post(f"/api/v1/rooms/{r_id}/join", headers=auth_header)

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "ROOM_NOT_FOUND"


def test_join_room_already_member_409(client, test_user, auth_header):
    """Test joining a room user is already in returns 409 ALREADY_IN_ROOM."""
    r_id = uuid.uuid4()
    from app.core.errors import ConflictError

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_user, \
         patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join_room:

        mock_get_user.return_value = test_user
        mock_join_room.side_effect = ConflictError("ALREADY_IN_ROOM", "User is already a member")

        response = client.post(f"/api/v1/rooms/{r_id}/join", headers=auth_header)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "ALREADY_IN_ROOM"
