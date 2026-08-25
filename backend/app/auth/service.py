from __future__ import annotations
"""
LinguaChat — Auth Service

Business logic for user authentication, registration, and session token issuance.
Implementation: Yousef Khairy — TASK-03-YOUSEF
See: docs/api-contract.md § 1 & 2, docs/security.md § 2, 3, 10
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.database.models.user import User
from app.database.session import get_db
from app.users import service as users_service
from app.users.schemas import UserCreate

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def register_user(
    db: AsyncSession,
    data: RegisterRequest,
) -> RegisterResponse:
    """
    Register a new user account.

    Raises:
        ConflictError (409): If username is already taken.
    """
    existing = await users_service.get_user_by_username(db, data.username)
    if existing:
        raise ConflictError(
            code="USERNAME_ALREADY_EXISTS",
            message=f"Username '{data.username}' is already registered",
        )

    user_create = UserCreate(
        username=data.username,
        password=data.password,
        preferred_language=data.preferred_language,
    )
    user = await users_service.create_user(db, user_create)

    return RegisterResponse(
        id=str(user.id),
        username=user.username,
        preferred_language=user.preferred_language,
        created_at=user.created_at.isoformat(),
    )


async def login_user(
    db: AsyncSession,
    data: LoginRequest,
) -> LoginResponse:
    """
    Authenticate user credentials and issue a signed JWT access token.

    Raises:
        UnauthorizedError (401): If credentials do not match or user is inactive.
    """
    user = await users_service.get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        # Generic message prevents user enumeration attacks (docs/security.md § 10)
        raise UnauthorizedError("Invalid username or password")

    if not user.is_active:
        raise UnauthorizedError("User account is inactive")

    expires_in_seconds = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "username": user.username,
            "preferred_language": user.preferred_language,
        },
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in_seconds,
    )


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
) -> User:
    """
    FastAPI security dependency to authenticate requests using Bearer JWT.

    Raises:
        UnauthorizedError (401): If token is missing, expired, or invalid.
    """
    if not token:
        raise UnauthorizedError("Missing authentication token")

    try:
        payload = decode_access_token(token)
    except HTTPException:
        raise UnauthorizedError("Could not validate credentials")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Could not validate credentials")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid token subject")

    user = await users_service.get_user_by_id(db, user_uuid)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    return user
