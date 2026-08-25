from __future__ import annotations
"""
LinguaChat — Auth Router

Defines POST /auth/register and POST /auth/login endpoints.
Implementation: Yousef Khairy — TASK-03-YOUSEF
See: docs/api-contract.md § 1 & 2
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)
from app.auth import service as auth_service
from app.database.models.user import User
from app.users.schemas import UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user account.
    Contract: docs/api-contract.md § 1. POST /auth/register
    """
    return await auth_service.register_user(db, data)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and obtain access token",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate user credentials and obtain JWT access token.
    Contract: docs/api-contract.md § 2. POST /auth/login
    """
    return await auth_service.login_user(db, data)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(auth_service.get_current_user),
) -> User:
    """
    Retrieve profile of the authenticated user.
    """
    return current_user
