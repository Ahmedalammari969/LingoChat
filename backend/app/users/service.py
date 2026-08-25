from __future__ import annotations
"""
LinguaChat — Users Database Service

Provides asynchronous CRUD operations for User entities.
Schema defined in: docs/database-schema.md § 1. users
Implementation: Yousef Khairy — TASK-02-YOUSEF
"""

import uuid
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database.models.user import User
from app.users.schemas import UserCreate, UserUpdate


async def get_user_by_id(
    db: AsyncSession,
    user_id: Union[uuid.UUID, str],
) -> Optional[User]:
    """
    Retrieve a user by their UUID identifier.

    Args:
        db: Async database session.
        user_id: User UUID or string representation.

    Returns:
        User model instance if found, None otherwise.
    """
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return None

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_username(
    db: AsyncSession,
    username: str,
) -> Optional[User]:
    """
    Retrieve a user by their unique username.

    Args:
        db: Async database session.
        username: Username to look up.

    Returns:
        User model instance if found, None otherwise.
    """
    if not username:
        return None
    query = select(User).where(User.username == username.strip())
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    user_in: UserCreate,
) -> User:
    """
    Create and persist a new user with bcrypt password hashing.

    Args:
        db: Async database session.
        user_in: Validated UserCreate schema.

    Returns:
        Persisted User ORM instance.
    """
    hashed = hash_password(user_in.password)
    user = User(
        username=user_in.username.strip(),
        hashed_password=hashed,
        preferred_language=user_in.preferred_language.strip().lower(),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user: User,
    user_in: UserUpdate,
) -> User:
    """
    Update an existing user's attributes (preferred language or password).

    Args:
        db: Async database session.
        user: Existing User ORM instance.
        user_in: UserUpdate schema.

    Returns:
        Updated User ORM instance.
    """
    if user_in.preferred_language is not None:
        user.preferred_language = user_in.preferred_language.strip().lower()

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user
