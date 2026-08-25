"""
LinguaChat — Security Utilities Unit Tests
Tests for TASK-02-YOUSEF
Schema Source of Truth: docs/security.md § 2 (Password Hashing) & § 3 (JWT)
"""

import uuid
from datetime import timedelta
import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    """Verify password hashing generates valid bcrypt hash and verifies correctly."""
    plain = "SuperSecretP@ssw0rd123"
    hashed = hash_password(plain)

    # Must not be plaintext
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    # Verification must succeed for correct password
    assert verify_password(plain, hashed) is True

    # Verification must fail for incorrect password
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(plain, "") is False


def test_password_hashing_salt_uniqueness():
    """Verify multiple hashes of the same password produce different salt hashes."""
    pwd = "SamePasswordEveryTime"
    hash1 = hash_password(pwd)
    hash2 = hash_password(pwd)

    assert hash1 != hash2
    assert verify_password(pwd, hash1) is True
    assert verify_password(pwd, hash2) is True


def test_jwt_create_and_decode_valid_token():
    """Verify JWT access token creation and decoding with claims."""
    user_id = str(uuid.uuid4())
    token = create_access_token(
        subject=user_id,
        extra_claims={"username": "alice", "preferred_language": "ar"},
    )

    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["username"] == "alice"
    assert payload["preferred_language"] == "ar"
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_expired_token_rejected():
    """Verify expired token raises 401 Unauthorized."""
    user_id = str(uuid.uuid4())
    # Create token that expired 10 minutes ago
    expired_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=-10),
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)

    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail


def test_jwt_tampered_token_rejected():
    """Verify tampered JWT signature is rejected with 401."""
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id)

    # Tamper with payload
    parts = token.split(".")
    tampered_token = f"{parts[0]}.eyJob3N0IjoiaGFja2VkIn0.{parts[2]}"

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(tampered_token)

    assert exc_info.value.status_code == 401


def test_jwt_invalid_secret_rejected():
    """Verify token signed with different secret is rejected with 401."""
    user_id = str(uuid.uuid4())
    fake_token = jwt.encode(
        {"sub": user_id, "exp": 9999999999},
        "wrong-secret-key-12345678901234567890",
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(fake_token)

    assert exc_info.value.status_code == 401
