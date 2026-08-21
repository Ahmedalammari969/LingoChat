"""
LinguaChat — Security Utilities (Skeleton)

Contains utility functions for password hashing and JWT operations.
Full implementation is the responsibility of Yousef Khairy (auth module).

See docs/security.md for security policy.
"""

# NOTE TO YOUSEF KHAIRY:
# Implement the following functions in this file as part of your auth task.
# Do NOT import app-specific models here to keep this module dependency-free.
# This module should only depend on: core/config.py and third-party crypto libraries.

# Required libraries (add to requirements.txt when implementing):
# - passlib[bcrypt]
# - python-jose[cryptography]

from app.core.config import settings  # noqa: F401 — used by implementer


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password: The user's plaintext password.

    Returns:
        A bcrypt hash string.

    Security: See docs/security.md § 2. Password Hashing.
    Implementation: Yousef Khairy — TASK: Authentication
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password:  The plaintext password to verify.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if password matches, False otherwise.

    Security: See docs/security.md § 2. Password Hashing.
    Implementation: Yousef Khairy — TASK: Authentication
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")


def create_access_token(subject: str) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The user ID (UUID string) to encode in the token.

    Returns:
        A signed JWT string.

    Security: See docs/security.md § 3. JWT.
    Implementation: Yousef Khairy — TASK: Authentication
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT string to decode.

    Returns:
        The decoded token payload dict.

    Raises:
        UnauthorizedError: If token is invalid, expired, or malformed.

    Security: See docs/security.md § 3. JWT.
    Implementation: Yousef Khairy — TASK: Authentication
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")
