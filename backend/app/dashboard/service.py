"""
LinguaChat — Dashboard Service (Skeleton)

Implementation: Yousef Khairy — TASK: Dashboard API
"""

from sqlalchemy.ext.asyncio import AsyncSession


async def get_system_stats(db: AsyncSession, active_connections: int = 0) -> dict:
    """
    Query aggregate system statistics from the database.

    Returns:
        {
            "total_users": int,
            "total_rooms": int,
            "total_messages": int,
            "total_translations": int,
            "active_connections": int
        }

    Notes:
    - active_connections is passed in from the WebSocket manager (not from DB).
    - All queries are read-only aggregations.
    - See docs/architecture.md § 3.8 Dashboard for boundary rules.

    Implementation: Yousef Khairy
    """
    raise NotImplementedError("Implement in dashboard task — Yousef Khairy")
