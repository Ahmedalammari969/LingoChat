"""
LinguaChat — Users Schemas (Pydantic)

Implementation: Yousef Khairy
"""

from pydantic import BaseModel


class UserPublic(BaseModel):
    """Public-safe user representation. Never includes hashed_password."""
    id: str
    username: str
    preferred_language: str
    created_at: str


class UpdatePreferredLanguage(BaseModel):
    preferred_language: str
