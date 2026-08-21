"""
LinguaChat — Auth Schemas (Pydantic)

Request/response schemas for authentication endpoints.
Endpoint contracts defined in: docs/api-contract.md
Implementation: Yousef Khairy — TASK: Authentication
"""

from pydantic import BaseModel, Field, field_validator
import re


class RegisterRequest(BaseModel):
    """POST /auth/register request body."""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    preferred_language: str = Field(..., min_length=2, max_length=10)

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, and underscores")
        return v


class RegisterResponse(BaseModel):
    """POST /auth/register success response."""

    id: str
    username: str
    preferred_language: str
    created_at: str


class LoginRequest(BaseModel):
    """POST /auth/login request body."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """POST /auth/login success response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
