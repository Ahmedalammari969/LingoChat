from __future__ import annotations
"""
LinguaChat — WebSocket Connection Manager

Manages active WebSocket connections per room, lifecycle, broadcasting, and heartbeats.
Implementation: Mohammed Al-Daees — TASK-02-MOHAMMED
Contract: docs/websocket-contract.md § Connection Lifecycle & Heartbeat
"""

import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Union
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active WebSocket connections organized by room.

    Responsibilities:
    - Track active connections per room in memory.
    - Full room isolation (messages in room A never reach room B).
    - Send individual (personal) messages and room broadcasts.
    - Custom recipient-specific broadcasting (e.g. translated per preferred language).
    - Heartbeat tracking and dead connection cleanup.
    - Total active connection counting for dashboard metrics.
    """

    def __init__(self) -> None:
        # Structure: room_id (str) -> user_id (str) -> dict containing connection details
        # {
        #   "room_id": {
        #       "user_id": {
        #           "ws": WebSocket,
        #           "username": str,
        #           "preferred_language": str,
        #           "last_heartbeat": float,
        #           "connected_at": float
        #       }
        #   }
        # }
        self._rooms: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        room_id: Union[str, uuid.UUID],
        user_id: Union[str, uuid.UUID],
        username: str,
        preferred_language: str = "en",
        accept_connection: bool = True,
    ) -> None:
        """
        Accept a WebSocket connection and register it in the room connection pool.

        Args:
            websocket: FastAPI WebSocket instance.
            room_id: UUID or string ID of the room.
            user_id: UUID or string ID of the connecting user.
            username: Display username of the user.
            preferred_language: ISO language code for message translations.
            accept_connection: Whether to call websocket.accept() (default True).
        """
        if accept_connection:
            try:
                await websocket.accept()
            except Exception as e:
                # If already accepted or failed, log and proceed with registration if alive
                logger.debug(f"WebSocket accept note: {e}")

        r_id = str(room_id)
        u_id = str(user_id)
        now = time.time()

        async with self._lock:
            # If user already had a stale connection in the room, replace it safely
            self._rooms[r_id][u_id] = {
                "ws": websocket,
                "username": username,
                "preferred_language": preferred_language or "en",
                "last_heartbeat": now,
                "connected_at": now,
            }

        logger.info(f"User '{username}' ({u_id}) connected to room '{r_id}'. Room count: {len(self._rooms[r_id])}")

    async def disconnect(
        self,
        websocket: Optional[WebSocket],
        room_id: Union[str, uuid.UUID],
        user_id: Optional[Union[str, uuid.UUID]] = None,
        username: Optional[str] = None,
    ) -> None:
        """
        Remove connection from room pool and clean up empty rooms.

        Args:
            websocket: WebSocket instance to remove (optional if user_id is provided).
            room_id: Room identifier.
            user_id: User identifier (optional if websocket is provided).
            username: Optional username for logging.
        """
        r_id = str(room_id)
        u_id = str(user_id) if user_id is not None else None

        async with self._lock:
            if r_id not in self._rooms:
                return

            room_dict = self._rooms[r_id]

            if u_id and u_id in room_dict:
                del room_dict[u_id]
            elif websocket:
                # Find by websocket instance
                keys_to_delete = [
                    uid for uid, conn in room_dict.items() if conn.get("ws") == websocket
                ]
                for k in keys_to_delete:
                    del room_dict[k]

            # Clean up empty room to avoid memory leak
            if len(room_dict) == 0:
                self._rooms.pop(r_id, None)

        logger.info(f"User disconnected from room '{r_id}'. Remaining in room: {len(self._rooms.get(r_id, {}))}")

    def record_heartbeat(
        self,
        room_id: Union[str, uuid.UUID],
        user_id: Union[str, uuid.UUID],
    ) -> bool:
        """
        Update the timestamp of the last received heartbeat ping.

        Returns:
            True if connection exists and heartbeat recorded, False otherwise.
        """
        r_id = str(room_id)
        u_id = str(user_id)

        if r_id in self._rooms and u_id in self._rooms[r_id]:
            self._rooms[r_id][u_id]["last_heartbeat"] = time.time()
            return True
        return False

    async def send_to_connection(
        self,
        websocket: WebSocket,
        message: Union[str, Dict[str, Any]],
    ) -> bool:
        """
        Send a message safely to a specific WebSocket connection.

        Args:
            websocket: Target WebSocket.
            message: JSON string or dictionary envelope.

        Returns:
            True on successful delivery, False if connection is broken.
        """
        msg_str = json.dumps(message, ensure_ascii=False) if isinstance(message, dict) else str(message)
        try:
            await websocket.send_text(msg_str)
            return True
        except Exception as e:
            logger.warning(f"Failed to send message to connection: {e}")
            return False

    async def send_personal_message(
        self,
        message: Union[str, Dict[str, Any]],
        websocket: WebSocket,
    ) -> bool:
        """Alias for send_to_connection."""
        return await self.send_to_connection(websocket=websocket, message=message)

    async def broadcast_to_room(
        self,
        room_id: Union[str, uuid.UUID],
        message: Union[str, Dict[str, Any]],
        exclude_connection: Optional[WebSocket] = None,
        exclude_user_id: Optional[Union[str, uuid.UUID]] = None,
    ) -> int:
        """
        Send a message to all active connections in a room.

        Args:
            room_id: Target room.
            message: Message envelope (dict or JSON string).
            exclude_connection: Optional WebSocket to exclude (e.g. sender).
            exclude_user_id: Optional user_id to exclude (e.g. sender).

        Returns:
            Count of successfully delivered messages.
        """
        r_id = str(room_id)
        ex_uid = str(exclude_user_id) if exclude_user_id is not None else None

        if r_id not in self._rooms or not self._rooms[r_id]:
            return 0

        msg_str = json.dumps(message, ensure_ascii=False) if isinstance(message, dict) else str(message)

        # Snapshot active connections to avoid dictionary mutation errors during iteration
        async with self._lock:
            connections = list(self._rooms[r_id].items())

        delivered_count = 0
        broken_uids: List[str] = []

        for uid, conn_info in connections:
            ws = conn_info.get("ws")
            if not ws:
                continue
            if exclude_connection and ws == exclude_connection:
                continue
            if ex_uid and uid == ex_uid:
                continue

            success = await self.send_to_connection(ws, msg_str)
            if success:
                delivered_count += 1
            else:
                broken_uids.append(uid)

        # Clean up any broken connections discovered during broadcast
        if broken_uids:
            async with self._lock:
                for b_uid in broken_uids:
                    if r_id in self._rooms and b_uid in self._rooms[r_id]:
                        del self._rooms[r_id][b_uid]
                if r_id in self._rooms and len(self._rooms[r_id]) == 0:
                    self._rooms.pop(r_id, None)

        return delivered_count

    async def broadcast_custom(
        self,
        room_id: Union[str, uuid.UUID],
        message_factory: Callable[[Dict[str, Any]], Union[str, Dict[str, Any], Any]],
        exclude_user_id: Optional[Union[str, uuid.UUID]] = None,
    ) -> int:
        """
        Broadcast tailored messages to each member in a room (e.g. translation per preferred language).

        Args:
            room_id: Target room.
            message_factory: Callable receiving user connection info dict and returning message.
            exclude_user_id: Optional user_id to skip.

        Returns:
            Count of successfully delivered messages.
        """
        r_id = str(room_id)
        ex_uid = str(exclude_user_id) if exclude_user_id is not None else None

        if r_id not in self._rooms or not self._rooms[r_id]:
            return 0

        async with self._lock:
            connections = list(self._rooms[r_id].items())

        delivered_count = 0
        broken_uids: List[str] = []

        for uid, conn_info in connections:
            if ex_uid and uid == ex_uid:
                continue
            ws = conn_info.get("ws")
            if not ws:
                continue

            try:
                # Allow message_factory to be async or sync
                if asyncio.iscoroutinefunction(message_factory):
                    custom_msg = await message_factory(conn_info)
                else:
                    custom_msg = message_factory(conn_info)

                if custom_msg is None:
                    continue

                success = await self.send_to_connection(ws, custom_msg)
                if success:
                    delivered_count += 1
                else:
                    broken_uids.append(uid)
            except Exception as e:
                logger.error(f"Error in custom broadcast for user {uid}: {e}")

        if broken_uids:
            async with self._lock:
                for b_uid in broken_uids:
                    if r_id in self._rooms and b_uid in self._rooms[r_id]:
                        del self._rooms[r_id][b_uid]
                if r_id in self._rooms and len(self._rooms[r_id]) == 0:
                    self._rooms.pop(r_id, None)

        return delivered_count

    def get_room_user_count(self, room_id: Union[str, uuid.UUID]) -> int:
        """Return number of active connections in a room."""
        r_id = str(room_id)
        return len(self._rooms.get(r_id, {}))

    def get_active_connections_count(self) -> int:
        """Return total count of active connections across all rooms."""
        return sum(len(room_conns) for room_conns in self._rooms.values())

    def is_user_in_room(
        self,
        room_id: Union[str, uuid.UUID],
        user_id: Union[str, uuid.UUID],
    ) -> bool:
        """Check if a specific user has an active connection in the room."""
        r_id = str(room_id)
        u_id = str(user_id)
        return r_id in self._rooms and u_id in self._rooms[r_id]

    def get_room_members(
        self,
        room_id: Union[str, uuid.UUID],
    ) -> List[Dict[str, Any]]:
        """Return list of active members in a room."""
        r_id = str(room_id)
        if r_id not in self._rooms:
            return []
        return [
            {
                "user_id": uid,
                "username": info["username"],
                "preferred_language": info["preferred_language"],
                "connected_at": info["connected_at"],
            }
            for uid, info in self._rooms[r_id].items()
        ]


# ── Singleton instance ─────────────────────────────────────────────────────────
# Import this instance in router.py and services
manager = ConnectionManager()
