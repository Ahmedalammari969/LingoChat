from __future__ import annotations
"""
LinguaChat — Security Utilities

Contains utility functions for password hashing and JWT operations.
Schema & Security Truth: docs/security.md § 2 (Password Hashing) & § 3 (JWT)
Implementation: Yousef Khairy — TASK-02-YOUSEF
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import uuid
import bcrypt

from fastapi import HTTPException, status
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt with cost factor >= 12.

    Args:
        plain_password: The user's plaintext password.

    Returns:
        A bcrypt hash string.
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")
    pwd_bytes = plain_password.encode("utf-8")
    # Truncate at 72 bytes as per bcrypt specification
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Args:
        plain_password: The plaintext password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if password matches, False otherwise.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        pwd_bytes = plain_password.encode("utf-8")
        if len(pwd_bytes) > 72:
            pwd_bytes = pwd_bytes[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: Union[str, uuid.UUID, Dict[str, Any]],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a signed JWT access token using HS256 algorithm.

    Args:
        subject: The user ID (UUID or string) or a dictionary of claims.
        expires_delta: Optional custom token expiration timedelta.
        extra_claims: Optional dictionary with additional claims (e.g., username, preferred_language).

    Returns:
        Signed JWT string.
    """
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode: Dict[str, Any] = {}
    if isinstance(subject, dict):
        to_encode.update(subject)
    else:
        to_encode["sub"] = str(subject)

    if extra_claims:
        to_encode.update(extra_claims)

    to_encode["iat"] = int(now.timestamp())
    to_encode["exp"] = int(expire.timestamp())

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: Raw JWT access token string.

    Returns:
        Decoded payload dictionary containing claims.

    Raises:
        HTTPException 401 if token is expired, invalid, or missing subject.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token or not isinstance(token, str):
        raise credentials_exception

    try:
        payload = jwt.decode(
            token.strip(),
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return payload
    except (ExpiredSignatureError, JWTClaimsError, JWTError, ValueError):
        raise credentials_exception
