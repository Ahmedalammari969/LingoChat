"""
LinguaChat — Users Schemas & Service Unit Tests
Tests for TASK-02-YOUSEF
"""

import uuid
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.users.schemas import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublic,
    TokenResponse,
)
from app.database.models.user import User


def test_user_create_validation_success():
    """Verify valid UserCreate data passes validation."""
    data = {
        "username": "ahmed_99",
        "preferred_language": "ar",
        "password": "valid_secure_password_123",
    }
    user = UserCreate(**data)
    assert user.username == "ahmed_99"
    assert user.preferred_language == "ar"
    assert user.password == "valid_secure_password_123"


def test_user_create_short_password_rejected():
    """Verify password shorter than 8 characters is rejected."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="validuser",
            preferred_language="en",
            password="123",  # Too short
        )


def test_user_create_invalid_username_characters_rejected():
    """Verify usernames with spaces or special characters are rejected."""
    invalid_usernames = ["user with spaces", "user@email.com", "user!#$", "ab"]
    for un in invalid_usernames:
        with pytest.raises(ValidationError):
            UserCreate(
                username=un,
                preferred_language="en",
                password="validpassword123",
            )


def test_user_response_excludes_hashed_password():
    """
    SECURITY TEST: Verify UserResponse cannot contain hashed_password field
    and serializes cleanly from ORM model.
    """
    u_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    orm_user = User(
        id=u_id,
        username="secure_user",
        hashed_password="bcrypt_hash_value_that_must_not_leak",
        preferred_language="fr",
        created_at=now,
        updated_at=now,
        is_active=True,
    )

    response = UserResponse.model_validate(orm_user)
    dumped = response.model_dump()

    assert dumped["id"] == u_id
    assert dumped["username"] == "secure_user"
    assert dumped["preferred_language"] == "fr"
    assert dumped["is_active"] is True
    assert "hashed_password" not in dumped


def test_token_response_schema():
    """Verify TokenResponse schema."""
    resp = TokenResponse(
        access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        token_type="bearer",
        expires_in=3600,
    )
    assert resp.token_type == "bearer"
    assert resp.expires_in == 3600
