from __future__ import annotations
"""
LinguaChat — Dashboard Router

Endpoint: GET /dashboard/stats
Implementation: Yousef Khairy — TASK-06-YOUSEF
Contract: docs/api-contract.md § 7. GET /dashboard/stats
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service as auth_service
from app.dashboard import service as dashboard_service
from app.database.models.user import User
from app.database.session import get_db
from app.websocket.manager import manager as ws_manager

router = APIRouter()


class DashboardStats(BaseModel):
    total_users: int
    total_rooms: int
    total_messages: int
    total_translations: int
    active_connections: int

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/stats",
    response_model=DashboardStats,
    status_code=status.HTTP_200_OK,
    summary="Get system aggregate statistics",
)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
) -> DashboardStats:
    """
    Retrieve aggregate statistics for LinguaChat system dashboard.
    Contract: docs/api-contract.md § 7. GET /dashboard/stats

    Requires valid Bearer JWT.
    """
    active_count = 0
    try:
        if hasattr(ws_manager, "get_active_connections_count"):
            active_count = ws_manager.get_active_connections_count()
    except Exception:
        active_count = 0

    stats = await dashboard_service.get_system_stats(db, active_connections=active_count)
    return DashboardStats(**stats)
