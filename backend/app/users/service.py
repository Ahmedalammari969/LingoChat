"""LinguaChat — Users Service (Skeleton) — Implementation: Yousef Khairy"""
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> dict:
    raise NotImplementedError("Implement — Yousef Khairy")

async def get_user_by_username(db: AsyncSession, username: str) -> dict:
    raise NotImplementedError("Implement — Yousef Khairy")
