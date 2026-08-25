"""
LinguaChat — Shared Test Configuration & Fixtures

Provides reusable fixtures for all unit and integration tests:
- Async TestClient with ASGI transport
- Sync TestClient for unit tests
- User creation helpers with JWT token generation
- Expired and fake token generators
- Mock database session factory

Implementation: Yousef Khairy — TASK-07-YOUSEF
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.database.models.user import User
from app.core.security import create_access_token, hash_password


# ── Sync TestClient ───────────────────────────────────────────────────────────

@pytest.fixture
def client() -> TestClient:
    """Provide a synchronous TestClient for unit-level endpoint tests."""
    return TestClient(app)


# ── Async TestClient ──────────────────────────────────────────────────────────

@pytest.fixture
async def async_client() -> AsyncClient:
    """Provide an asynchronous httpx.AsyncClient for integration tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# ── User Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def test_user_password() -> str:
    """Raw plaintext password for test user."""
    return "TestPassword_123"


@pytest.fixture
def test_user(test_user_password: str) -> User:
    """
    Create a mock User ORM object with realistic defaults.
    Useful for patching service layer calls.
    """
    now = datetime.now(timezone.utc)
    return User(
        id=uuid.uuid4(),
        username="test_user_yousef",
        hashed_password=hash_password(test_user_password),
        preferred_language="ar",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@pytest.fixture
def second_test_user() -> User:
    """
    Create a second mock User for multi-user scenarios
    (room joining, membership checks, etc.).
    """
    now = datetime.now(timezone.utc)
    return User(
        id=uuid.uuid4(),
        username="second_tester",
        hashed_password=hash_password("SecondPass_456"),
        preferred_language="en",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


# ── Token Fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def valid_token(test_user: User) -> str:
    """Generate a valid JWT access token for test_user."""
    return create_access_token(
        subject=str(test_user.id),
        extra_claims={
            "username": test_user.username,
            "preferred_language": test_user.preferred_language,
        },
    )


@pytest.fixture
def auth_header(valid_token: str) -> dict:
    """Standard Authorization header with valid Bearer token."""
    return {"Authorization": f"Bearer {valid_token}"}


@pytest.fixture
def expired_token(test_user: User) -> str:
    """Generate an expired JWT access token (expired 30 minutes ago)."""
    return create_access_token(
        subject=str(test_user.id),
        expires_delta=timedelta(minutes=-30),
    )


@pytest.fixture
def expired_auth_header(expired_token: str) -> dict:
    """Authorization header with an expired Bearer token."""
    return {"Authorization": f"Bearer {expired_token}"}


@pytest.fixture
def invalid_token() -> str:
    """A completely invalid/fake JWT string."""
    return "eyJhbGciOiJIUzI1NiJ9.FAKE_PAYLOAD.FAKE_SIG"


@pytest.fixture
def invalid_auth_header(invalid_token: str) -> dict:
    """Authorization header with an invalid/fake Bearer token."""
    return {"Authorization": f"Bearer {invalid_token}"}


@pytest.fixture
def second_user_token(second_test_user: User) -> str:
    """Generate a valid JWT access token for the second test user."""
    return create_access_token(
        subject=str(second_test_user.id),
        extra_claims={
            "username": second_test_user.username,
            "preferred_language": second_test_user.preferred_language,
        },
    )


@pytest.fixture
def second_auth_header(second_user_token: str) -> dict:
    """Authorization header for the second test user."""
    return {"Authorization": f"Bearer {second_user_token}"}
