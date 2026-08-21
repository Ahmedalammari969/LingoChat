from __future__ import annotations
"""
LinguaChat — WebSocket Connection Manager (Skeleton)

Manages active WebSocket connections per room.
Implementation: Mohammed Al-Daees — TASK: WebSocket Gateway
See: docs/websocket-contract.md, docs/architecture.md
"""

import uuid
from collections import defaultdict
from typing import Optional
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket connections organized by room.

    Responsibilities:
    - Track which connections belong to which room.
    - Broadcast messages to all members of a room.
    - Handle connect/disconnect lifecycle.
    - Send LEAVE events when a user disconnects.

    Implementation: Mohammed Al-Daees
    """

    def __init__(self):
        # room_id -> set of (user_id, WebSocket) tuples
        self._rooms: dict[str, set] = defaultdict(set)

    async def connect(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: uuid.UUID,
        username: str,
    ) -> None:
        """
        Accept a WebSocket connection and register it in the room.
        Broadcast JOIN message to all room members.
        Implementation: Mohammed Al-Daees
        """
        raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")

    async def disconnect(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: uuid.UUID,
        username: str,
    ) -> None:
        """
        Remove connection from room and broadcast LEAVE message.
        Implementation: Mohammed Al-Daees
        """
        raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")

    async def broadcast_to_room(
        self,
        room_id: str,
        message: str,
        exclude_connection: Optional[WebSocket] = None,
    ) -> None:
        """
        Send a message string to all active connections in a room.
        Optionally exclude the sender's connection.
        Implementation: Mohammed Al-Daees
        """
        raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")

    async def send_to_connection(self, websocket: WebSocket, message: str) -> None:
        """Send a message to a specific connection only."""
        raise NotImplementedError("Implement in WebSocket task — Mohammed Al-Daees")

    def get_room_user_count(self, room_id: str) -> int:
        """Return number of active connections in a room."""
        return len(self._rooms.get(room_id, set()))


# ── Singleton instance ─────────────────────────────────────────────────────────
# Import this instance in router.py
manager = ConnectionManager()
