"""
LinguaChat — Auth Router (Skeleton)

Defines POST /auth/register and POST /auth/login endpoints.
Implementation: Yousef Khairy — TASK: Authentication
See: docs/api-contract.md § 1 & 2
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse
from app.auth import service as auth_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user.
    Contract: docs/api-contract.md § 1. POST /auth/register
    """
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate user and return JWT.
    Contract: docs/api-contract.md § 2. POST /auth/login
    """
    return await auth_service.login_user(db, data)
