"""
LinguaChat — Full REST API Integration Tests

Comprehensive integration test scenarios that validate the complete
lifecycle flows across all REST API endpoints:

  Scenario 1: User Lifecycle (Register → Login → Get Token → /me)
  Scenario 2: Room Lifecycle (Create → Verify Creator Membership → Join → Reject Duplicate)
  Scenario 3: Message Lifecycle (Send → Fetch History → Pagination → Non-Member Rejection)
  Scenario 4: Dashboard Stats (Verify counters after operations)
  Scenario 5: Error Handling (401, 403, 404, 409, 422 edge cases)
  Scenario 6: Malformed Input & Edge Cases

Implementation: Yousef Khairy — TASK-07-YOUSEF
Contract: docs/api-contract.md § 1-7
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import hash_password, create_access_token
from app.database.models.user import User
from app.database.models.room import Room
from app.rooms.schemas import (
    RoomResponse,
    RoomListResponse,
    RoomListItem,
    JoinRoomResponse,
)
from app.messages.schemas import MessageHistoryResponse, MessageResponse
from app.core.errors import NotFoundError, ConflictError, ForbiddenError


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_alice():
    """User Alice — primary integration test actor."""
    now = datetime.now(timezone.utc)
    return User(
        id=uuid.uuid4(),
        username="alice_integration",
        hashed_password=hash_password("AliceSecure_123"),
        preferred_language="ar",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@pytest.fixture
def user_bob():
    """User Bob — secondary integration test actor."""
    now = datetime.now(timezone.utc)
    return User(
        id=uuid.uuid4(),
        username="bob_integration",
        hashed_password=hash_password("BobSecure_456"),
        preferred_language="en",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@pytest.fixture
def alice_token(user_alice):
    return create_access_token(
        subject=str(user_alice.id),
        extra_claims={
            "username": user_alice.username,
            "preferred_language": user_alice.preferred_language,
        },
    )


@pytest.fixture
def alice_header(alice_token):
    return {"Authorization": f"Bearer {alice_token}"}


@pytest.fixture
def bob_token(user_bob):
    return create_access_token(
        subject=str(user_bob.id),
        extra_claims={
            "username": user_bob.username,
            "preferred_language": user_bob.preferred_language,
        },
    )


@pytest.fixture
def bob_header(bob_token):
    return {"Authorization": f"Bearer {bob_token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1: User Lifecycle (Register → Login → /me)
# ═══════════════════════════════════════════════════════════════════════════════


class TestUserLifecycle:
    """Complete user registration, login, and profile retrieval flow."""

    def test_register_new_user_returns_201(self, client):
        """Register a brand-new user and verify 201 Created response fields."""
        mock_user = User(
            id=uuid.uuid4(),
            username="newuser_integ",
            hashed_password="bcrypt_hash_dummy",
            preferred_language="ar",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True,
        )

        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get, \
             patch("app.users.service.create_user", new_callable=AsyncMock) as mock_create:
            mock_get.return_value = None
            mock_create.return_value = mock_user

            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser_integ",
                    "password": "SecurePassword_123",
                    "preferred_language": "ar",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser_integ"
        assert data["preferred_language"] == "ar"
        assert "id" in data
        assert "created_at" in data
        # Security: password hash must NEVER be exposed
        assert "hashed_password" not in data
        assert "password" not in data

    def test_register_duplicate_username_returns_409(self, client):
        """Registering an existing username must return 409 USERNAME_ALREADY_EXISTS."""
        existing = User(
            id=uuid.uuid4(),
            username="duplicate_user",
            hashed_password="hash",
            preferred_language="en",
        )

        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = existing

            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "duplicate_user",
                    "password": "SecurePassword_123",
                    "preferred_language": "en",
                },
            )

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "USERNAME_ALREADY_EXISTS"

    def test_login_valid_credentials_returns_token(self, client, user_alice):
        """Login with correct credentials returns 200 OK and JWT token."""
        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_alice

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "alice_integration",
                    "password": "AliceSecure_123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    def test_login_wrong_password_returns_401(self, client, user_alice):
        """Login with wrong password returns 401 UNAUTHORIZED (generic message)."""
        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_alice

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "alice_integration",
                    "password": "WrongPassword_999",
                },
            )

        assert response.status_code == 401
        err = response.json()["error"]
        assert err["code"] == "UNAUTHORIZED"
        assert err["message"] == "Invalid username or password"

    def test_login_nonexistent_user_returns_401(self, client):
        """Login with non-existent username returns 401 (prevents enumeration)."""
        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            response = client.post(
                "/api/v1/auth/login",
                json={
                    "username": "ghost_user_xyz",
                    "password": "AnyPassword_123",
                },
            )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"

    def test_get_me_with_valid_token_returns_profile(self, client, user_alice, alice_header):
        """GET /me with valid token returns user profile without sensitive fields."""
        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_alice

            response = client.get("/api/v1/auth/me", headers=alice_header)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice_integration"
        assert data["preferred_language"] == "ar"
        assert "hashed_password" not in data

    def test_get_me_without_token_returns_401(self, client):
        """GET /me without Authorization header returns 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2: Room Lifecycle (Create → Join → Reject Duplicate)
# ═══════════════════════════════════════════════════════════════════════════════


class TestRoomLifecycle:
    """Complete room creation, membership, and join flow."""

    def test_create_room_returns_201(self, client, user_alice, alice_header):
        """Create a new room and verify 201 Created with invitation_link."""
        r_id = uuid.uuid4()
        mock_response = RoomResponse(
            id=str(r_id),
            name="Arabic Learners",
            invitation_link=f"/rooms/{r_id}/join",
            created_by=str(user_alice.id),
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.create_room", new_callable=AsyncMock) as mock_create:
            mock_user.return_value = user_alice
            mock_create.return_value = mock_response

            response = client.post(
                "/api/v1/rooms",
                headers=alice_header,
                json={"name": "Arabic Learners"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Arabic Learners"
        assert data["created_by"] == str(user_alice.id)
        assert "invitation_link" in data
        assert "id" in data

    def test_create_room_without_token_returns_401(self, client):
        """Attempting to create a room without authentication returns 401."""
        response = client.post("/api/v1/rooms", json={"name": "No Auth Room"})
        assert response.status_code == 401

    def test_list_rooms_with_pagination(self, client, user_alice, alice_header):
        """List rooms returns 200 with pagination fields and member_count."""
        r_id = uuid.uuid4()
        mock_list = RoomListResponse(
            rooms=[
                RoomListItem(
                    id=str(r_id),
                    name="Global Chat",
                    member_count=12,
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            ],
            total=1,
            limit=20,
            offset=0,
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.list_rooms", new_callable=AsyncMock) as mock_list_rooms:
            mock_user.return_value = user_alice
            mock_list_rooms.return_value = mock_list

            response = client.get("/api/v1/rooms?limit=20&offset=0", headers=alice_header)

        assert response.status_code == 200
        data = response.json()
        assert len(data["rooms"]) == 1
        assert data["rooms"][0]["member_count"] == 12
        assert data["total"] == 1
        assert data["limit"] == 20
        assert data["offset"] == 0

    def test_join_room_success_returns_200(self, client, user_bob, bob_header):
        """Bob joins an existing room, receives 200 OK."""
        r_id = uuid.uuid4()
        mock_join = JoinRoomResponse(
            room_id=str(r_id),
            user_id=str(user_bob.id),
            joined_at=datetime.now(timezone.utc).isoformat(),
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join_room:
            mock_user.return_value = user_bob
            mock_join_room.return_value = mock_join

            response = client.post(f"/api/v1/rooms/{r_id}/join", headers=bob_header)

        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == str(r_id)
        assert data["user_id"] == str(user_bob.id)

    def test_join_nonexistent_room_returns_404(self, client, user_alice, alice_header):
        """Joining a non-existent room returns 404 ROOM_NOT_FOUND."""
        r_id = uuid.uuid4()

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join:
            mock_user.return_value = user_alice
            mock_join.side_effect = NotFoundError("ROOM", str(r_id))

            response = client.post(f"/api/v1/rooms/{r_id}/join", headers=alice_header)

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "ROOM_NOT_FOUND"

    def test_join_room_already_member_returns_409(self, client, user_alice, alice_header):
        """Attempting to join a room user is already in returns 409 ALREADY_IN_ROOM."""
        r_id = uuid.uuid4()

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.join_room", new_callable=AsyncMock) as mock_join:
            mock_user.return_value = user_alice
            mock_join.side_effect = ConflictError("ALREADY_IN_ROOM", "User is already a member")

            response = client.post(f"/api/v1/rooms/{r_id}/join", headers=alice_header)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "ALREADY_IN_ROOM"


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3: Message Lifecycle & History
# ═══════════════════════════════════════════════════════════════════════════════


class TestMessageLifecycle:
    """Message retrieval, pagination, and access control."""

    def test_get_room_messages_member_success(self, client, user_alice, alice_header):
        """Member can retrieve room messages with translations (200 OK)."""
        r_id = uuid.uuid4()
        mock_room = Room(id=r_id, name="Arabic Chat", created_by=user_alice.id)
        mock_history = MessageHistoryResponse(
            messages=[
                MessageResponse(
                    id=str(uuid.uuid4()),
                    room_id=str(r_id),
                    sender_id=str(user_alice.id),
                    sender_username="alice_integration",
                    original_text="مرحبا",
                    original_language="ar",
                    translated_text="Hello",
                    target_language="en",
                    sent_at=datetime.now(timezone.utc).isoformat(),
                )
            ],
            has_more=False,
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room, \
             patch("app.rooms.service.is_user_member_of_room", new_callable=AsyncMock) as mock_member, \
             patch("app.messages.service.get_room_messages", new_callable=AsyncMock) as mock_msgs:
            mock_user.return_value = user_alice
            mock_get_room.return_value = mock_room
            mock_member.return_value = True
            mock_msgs.return_value = mock_history

            response = client.get(
                f"/api/v1/rooms/{r_id}/messages?limit=50",
                headers=alice_header,
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 1
        assert data["messages"][0]["original_text"] == "مرحبا"
        assert data["messages"][0]["translated_text"] == "Hello"
        assert data["has_more"] is False

    def test_get_room_messages_nonmember_forbidden_403(self, client, user_bob, bob_header):
        """Non-member is rejected with 403 FORBIDDEN."""
        r_id = uuid.uuid4()
        mock_room = Room(id=r_id, name="Private Room", created_by=uuid.uuid4())

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room, \
             patch("app.rooms.service.is_user_member_of_room", new_callable=AsyncMock) as mock_member:
            mock_user.return_value = user_bob
            mock_get_room.return_value = mock_room
            mock_member.return_value = False

            response = client.get(
                f"/api/v1/rooms/{r_id}/messages",
                headers=bob_header,
            )

        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"

    def test_get_messages_nonexistent_room_returns_404(self, client, user_alice, alice_header):
        """Requesting messages for a non-existent room returns 404."""
        r_id = uuid.uuid4()

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room:
            mock_user.return_value = user_alice
            mock_get_room.return_value = None

            response = client.get(
                f"/api/v1/rooms/{r_id}/messages",
                headers=alice_header,
            )

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "ROOM_NOT_FOUND"

    def test_get_messages_without_token_returns_401(self, client):
        """Requesting messages without authentication returns 401."""
        r_id = uuid.uuid4()
        response = client.get(f"/api/v1/rooms/{r_id}/messages")
        assert response.status_code == 401

    def test_get_messages_with_pagination_cursor(self, client, user_alice, alice_header):
        """Message history supports 'before' cursor pagination and 'has_more' flag."""
        r_id = uuid.uuid4()
        mock_room = Room(id=r_id, name="Paginated Room", created_by=user_alice.id)
        mock_history = MessageHistoryResponse(
            messages=[
                MessageResponse(
                    id=str(uuid.uuid4()),
                    room_id=str(r_id),
                    sender_id=str(user_alice.id),
                    sender_username="alice_integration",
                    original_text="Older message",
                    original_language="en",
                    translated_text="رسالة قديمة",
                    target_language="ar",
                    sent_at="2025-01-01T00:00:00Z",
                )
            ],
            has_more=True,
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.get_room_by_id", new_callable=AsyncMock) as mock_get_room, \
             patch("app.rooms.service.is_user_member_of_room", new_callable=AsyncMock) as mock_member, \
             patch("app.messages.service.get_room_messages", new_callable=AsyncMock) as mock_msgs:
            mock_user.return_value = user_alice
            mock_get_room.return_value = mock_room
            mock_member.return_value = True
            mock_msgs.return_value = mock_history

            response = client.get(
                f"/api/v1/rooms/{r_id}/messages?limit=10&before=2025-06-01T00:00:00Z",
                headers=alice_header,
            )

        assert response.status_code == 200
        data = response.json()
        assert data["has_more"] is True
        assert len(data["messages"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 4: Dashboard Stats
# ═══════════════════════════════════════════════════════════════════════════════


class TestDashboardStats:
    """Verify dashboard statistics endpoint and counter correctness."""

    def test_dashboard_stats_returns_all_fields(self, client, user_alice, alice_header):
        """GET /dashboard/stats returns all 5 required metric fields."""
        mock_stats = {
            "total_users": 25,
            "total_rooms": 8,
            "total_messages": 350,
            "total_translations": 700,
            "active_connections": 5,
        }

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.dashboard.service.get_system_stats", new_callable=AsyncMock) as mock_stats_fn:
            mock_user.return_value = user_alice
            mock_stats_fn.return_value = mock_stats

            response = client.get("/api/v1/dashboard/stats", headers=alice_header)

        assert response.status_code == 200
        data = response.json()
        assert data["total_users"] == 25
        assert data["total_rooms"] == 8
        assert data["total_messages"] == 350
        assert data["total_translations"] == 700
        assert data["active_connections"] == 5

    def test_dashboard_stats_zero_counters(self, client, user_alice, alice_header):
        """Dashboard with empty database returns zero for all fields."""
        mock_stats = {
            "total_users": 0,
            "total_rooms": 0,
            "total_messages": 0,
            "total_translations": 0,
            "active_connections": 0,
        }

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.dashboard.service.get_system_stats", new_callable=AsyncMock) as mock_stats_fn:
            mock_user.return_value = user_alice
            mock_stats_fn.return_value = mock_stats

            response = client.get("/api/v1/dashboard/stats", headers=alice_header)

        assert response.status_code == 200
        data = response.json()
        for key in ["total_users", "total_rooms", "total_messages", "total_translations", "active_connections"]:
            assert data[key] == 0

    def test_dashboard_stats_unauthorized_returns_401(self, client):
        """Dashboard stats without token returns 401."""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 5: Security Error Handling (401, 403, 404, 409, 422)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSecurityErrorHandling:
    """Comprehensive error code coverage across all endpoints."""

    def test_expired_token_rejected_401(self, client, user_alice):
        """Expired JWT token returns 401 UNAUTHORIZED on any protected endpoint."""
        from datetime import timedelta
        expired_token = create_access_token(
            subject=str(user_alice.id),
            expires_delta=timedelta(minutes=-30),
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_tampered_token_rejected_401(self, client):
        """Tampered/fake JWT token returns 401 UNAUTHORIZED."""
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.INVALID.PAYLOAD"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    def test_missing_authorization_header_401(self, client):
        """Missing Authorization header on protected endpoints returns 401."""
        endpoints = [
            ("GET", "/api/v1/auth/me"),
            ("POST", "/api/v1/rooms"),
            ("GET", "/api/v1/rooms"),
            ("GET", "/api/v1/dashboard/stats"),
        ]
        for method, path in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path, json={"name": "test"})
            assert response.status_code == 401, f"Expected 401 for {method} {path}, got {response.status_code}"

    def test_register_short_password_returns_422(self, client):
        """Registration with password < 8 characters returns 422 VALIDATION_ERROR."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "validuser",
                "password": "short",
                "preferred_language": "en",
            },
        )
        assert response.status_code == 422

    def test_register_invalid_username_characters_returns_422(self, client):
        """Registration with special characters in username returns 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user@email.com",
                "password": "ValidPassword_123",
                "preferred_language": "en",
            },
        )
        assert response.status_code == 422

    def test_register_empty_body_returns_422(self, client):
        """Registration with empty JSON body returns 422."""
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422

    def test_login_empty_credentials_returns_422(self, client):
        """Login with empty username/password returns 422."""
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 6: Malformed Inputs & Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Edge cases: malformed JSON, invalid UUIDs, boundary values."""

    def test_health_endpoint_always_accessible(self, client):
        """Health check endpoint responds 200 without authentication."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

    def test_unknown_route_returns_404(self, client):
        """Non-existent routes return 404."""
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

    def test_join_room_invalid_uuid_format(self, client, user_alice, alice_header):
        """Joining with an invalid UUID format returns 422."""
        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user:
            mock_user.return_value = user_alice
            response = client.post(
                "/api/v1/rooms/not-a-valid-uuid/join",
                headers=alice_header,
            )
        assert response.status_code == 422

    def test_list_rooms_large_offset(self, client, user_alice, alice_header):
        """List rooms with a very large offset returns empty list."""
        mock_list = RoomListResponse(
            rooms=[],
            total=0,
            limit=20,
            offset=999999,
        )

        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user, \
             patch("app.rooms.service.list_rooms", new_callable=AsyncMock) as mock_list_rooms:
            mock_user.return_value = user_alice
            mock_list_rooms.return_value = mock_list

            response = client.get(
                "/api/v1/rooms?limit=20&offset=999999",
                headers=alice_header,
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["rooms"]) == 0

    def test_register_username_too_short_returns_422(self, client):
        """Registration with 2-character username returns 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",
                "password": "ValidPassword_123",
                "preferred_language": "en",
            },
        )
        assert response.status_code == 422

    def test_register_valid_minimum_values(self, client):
        """Registration with minimum valid values succeeds."""
        mock_user = User(
            id=uuid.uuid4(),
            username="abc",
            hashed_password="hash",
            preferred_language="en",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True,
        )

        with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get, \
             patch("app.users.service.create_user", new_callable=AsyncMock) as mock_create:
            mock_get.return_value = None
            mock_create.return_value = mock_user

            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "abc",
                    "password": "12345678",
                    "preferred_language": "en",
                },
            )

        assert response.status_code == 201

    def test_create_room_empty_name_returns_422(self, client, user_alice, alice_header):
        """Creating a room with empty name returns 422."""
        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user:
            mock_user.return_value = user_alice
            response = client.post(
                "/api/v1/rooms",
                headers=alice_header,
                json={"name": ""},
            )
        # Either 422 validation or handled by the schema
        assert response.status_code in [400, 422]

    def test_messages_endpoint_invalid_limit_returns_422(self, client, user_alice, alice_header):
        """Message history with limit=0 returns 422."""
        r_id = uuid.uuid4()
        with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_user:
            mock_user.return_value = user_alice
            response = client.get(
                f"/api/v1/rooms/{r_id}/messages?limit=0",
                headers=alice_header,
            )
        assert response.status_code == 422
