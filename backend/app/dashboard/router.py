"""
LinguaChat — Dashboard Service & Router (Skeleton)

Implementation: Yousef Khairy — TASK: Dashboard API
See: docs/api-contract.md § 7. GET /dashboard/stats
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database.session import get_db

router = APIRouter()


class DashboardStats(BaseModel):
    total_users: int
    total_rooms: int
    total_messages: int
    total_translations: int
    active_connections: int


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user),  # add when auth is implemented
) -> DashboardStats:
    """
    Get aggregate system statistics.
    Contract: docs/api-contract.md § 7. GET /dashboard/stats
    Implementation: Yousef Khairy
    """
    raise NotImplementedError("Implement in dashboard task — Yousef Khairy")
