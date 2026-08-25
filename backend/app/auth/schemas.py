from __future__ import annotations
"""
LinguaChat — Auth Schemas (Pydantic)

Request/response schemas for authentication endpoints.
Endpoint contracts defined in: docs/api-contract.md § 1 & 2
Implementation: Yousef Khairy — TASK-03-YOUSEF
"""

import re
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
    """POST /auth/register request body."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Alphanumeric characters and underscores only",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plaintext password, minimum 8 characters",
    )
    preferred_language: str = Field(
        default="en",
        min_length=2,
        max_length=10,
        description="ISO 639-1 language code (e.g., 'en', 'ar', 'fr')",
    )

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v


class RegisterResponse(BaseModel):
    """POST /auth/register success response (201 Created)."""

    id: str
    username: str
    preferred_language: str
    created_at: str


class LoginRequest(BaseModel):
    """POST /auth/login request body."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """POST /auth/login success response (200 OK)."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
