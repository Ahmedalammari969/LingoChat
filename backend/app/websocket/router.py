"""
LinguaChat — WebSocket Router (Skeleton)

Endpoint: /ws/{room_id}
Implementation: Mohammed Al-Daees — TASK: WebSocket Gateway
See: docs/websocket-contract.md
"""

import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: uuid.UUID,
    token: str = Query(..., description="JWT access token"),
) -> None:
    """
    WebSocket endpoint for real-time room messaging.

    Connection flow:
    1. Validate JWT token → close with 4001 if invalid.
    2. Validate room membership → close with 4003 if not member.
    3. Register connection via manager.connect().
    4. Message loop: receive → parse → process → broadcast.
    5. On disconnect: manager.disconnect().

    Implementation: Mohammed Al-Daees
    See: docs/websocket-contract.md § Connection Lifecycle
    """
    raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")
