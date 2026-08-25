from __future__ import annotations
"""
LinguaChat — Users Pydantic Schemas

Schema defined in: docs/api-contract.md § 1, 2, 7 & docs/database-schema.md § 1
Implementation: Yousef Khairy — TASK-02-YOUSEF
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Alphanumeric characters and underscores only",
    )
    preferred_language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code (e.g., 'en', 'ar', 'fr')",
    )


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password, minimum 8 characters",
    )


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    preferred_language: Optional[str] = Field(
        None,
        min_length=2,
        max_length=10,
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
    )


class UpdatePreferredLanguage(BaseModel):
    """Schema for changing preferred language."""
    preferred_language: str = Field(
        ...,
        min_length=2,
        max_length=10,
    )


class UserResponse(UserBase):
    """
    Public user representation returned by API.
    SECURITY: hashed_password MUST NEVER be included in this schema.
    """
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserPublic(BaseModel):
    """Minimal public user representation for members list and chat cards."""
    id: uuid.UUID
    username: str
    preferred_language: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT token response schema for login and registration."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
