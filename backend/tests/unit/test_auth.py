"""
LinguaChat — Authentication API Unit & Integration Tests
Tests for TASK-03-YOUSEF
Contract: docs/api-contract.md § 1 & 2
"""

import uuid
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.database.models.user import User
from app.core.security import hash_password, create_access_token


@pytest.fixture
def client():
    return TestClient(app)


def test_register_user_success(client):
    """Test successful user registration returns 201 Created and public user fields."""
    mock_user = User(
        id=uuid.uuid4(),
        username="newuser123",
        hashed_password="bcrypt_hashed_dummy",
        preferred_language="ar",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )

    with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None  # No existing user

        with patch("app.users.service.create_user", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_user

            payload = {
                "username": "newuser123",
                "password": "securepassword123",
                "preferred_language": "ar",
            }
            response = client.post("/api/v1/auth/register", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert data["username"] == "newuser123"
            assert data["preferred_language"] == "ar"
            assert "id" in data
            assert "created_at" in data
            assert "hashed_password" not in data
            assert "password" not in data


def test_register_duplicate_username_conflict(client):
    """Test registering existing username returns 409 Conflict."""
    existing_user = User(
        id=uuid.uuid4(),
        username="existinguser",
        hashed_password="hash",
        preferred_language="en",
    )

    with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = existing_user

        payload = {
            "username": "existinguser",
            "password": "securepassword123",
            "preferred_language": "en",
        }
        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 409
        err = response.json()["error"]
        assert err["code"] == "USERNAME_ALREADY_EXISTS"


def test_register_short_password_rejected(client):
    """Test registration with password < 8 characters returns 422."""
    payload = {
        "username": "validuser",
        "password": "123",  # Short password
        "preferred_language": "en",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client):
    """Test valid credentials login returns 200 OK and JWT access token."""
    raw_password = "CorrectPassword123"
    hashed = hash_password(raw_password)

    user = User(
        id=uuid.uuid4(),
        username="loginuser",
        hashed_password=hashed,
        preferred_language="fr",
        is_active=True,
    )

    with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user

        payload = {
            "username": "loginuser",
            "password": raw_password,
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0


def test_login_wrong_password_rejected(client):
    """Test wrong password returns 401 Unauthorized with generic error message."""
    user = User(
        id=uuid.uuid4(),
        username="loginuser",
        hashed_password=hash_password("RealPassword123"),
        preferred_language="en",
        is_active=True,
    )

    with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = user

        payload = {
            "username": "loginuser",
            "password": "WrongPassword123",
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        err = response.json()["error"]
        assert err["code"] == "UNAUTHORIZED"
        assert err["message"] == "Invalid username or password"


def test_login_nonexistent_user_rejected(client):
    """Test login with non-existent username returns 401 Unauthorized."""
    with patch("app.users.service.get_user_by_username", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        payload = {
            "username": "ghostuser",
            "password": "AnyPassword123",
        }
        response = client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        err = response.json()["error"]
        assert err["code"] == "UNAUTHORIZED"


def test_get_me_protected_endpoint(client):
    """Test /me endpoint returns user profile when valid token provided."""
    u_id = uuid.uuid4()
    user = User(
        id=u_id,
        username="alice",
        hashed_password="hash",
        preferred_language="ar",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_active=True,
    )

    token = create_access_token(subject=str(u_id))

    with patch("app.users.service.get_user_by_id", new_callable=AsyncMock) as mock_get_id:
        mock_get_id.return_value = user

        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice"
        assert data["preferred_language"] == "ar"
        assert "hashed_password" not in data
