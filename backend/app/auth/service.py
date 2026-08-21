"""
LinguaChat — Auth Service (Skeleton)

Business logic for user authentication.
Implementation: Yousef Khairy — TASK: Authentication
See: docs/api-contract.md, docs/security.md
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import RegisterRequest, RegisterResponse, LoginRequest, LoginResponse


async def register_user(
    db: AsyncSession,
    data: RegisterRequest,
) -> RegisterResponse:
    """
    Register a new user.

    Steps (to implement):
    1. Check if username already exists → raise ConflictError("USERNAME_ALREADY_EXISTS", ...)
    2. Hash password using core/security.py:hash_password()
    3. Create User ORM record
    4. Commit and return RegisterResponse

    Raises:
        ConflictError: If username is already taken.
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")


async def login_user(
    db: AsyncSession,
    data: LoginRequest,
) -> LoginResponse:
    """
    Authenticate a user and return a JWT access token.

    Steps (to implement):
    1. Find user by username → raise UnauthorizedError on not found
    2. Verify password using core/security.py:verify_password()
       → raise UnauthorizedError("INVALID_CREDENTIALS") on mismatch
       (Use generic message — do not reveal whether username or password was wrong)
    3. Create access token using core/security.py:create_access_token()
    4. Return LoginResponse

    Security: See docs/security.md § 10. Error Handling.
    """
    raise NotImplementedError("Implement in auth task — Yousef Khairy")
