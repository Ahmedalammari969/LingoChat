from __future__ import annotations
"""
LinguaChat — WebSocket Router

Endpoint: ws://localhost:8000/ws/{room_id}?token=<access_token>
Implementation: Mohammed Al-Daees — TASK-03-MOHAMMED
Contract: docs/websocket-contract.md § Connection Lifecycle & Close Codes
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Union

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from app.core.config import settings
from app.websocket.manager import manager
from app.websocket.protocol import (
    WSMessageType,
    WSErrorCode,
    parse_and_validate_message,
    create_error_message,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Dependency Hooks for Room & Membership Verification ────────────────────────
# In unit tests or decoupled testing, these hooks can be mocked/overridden.
_room_validator: Optional[Callable[[str], bool]] = None
_membership_validator: Optional[Callable[[str, str], bool]] = None


def set_room_validator(func: Optional[Callable[[str], bool]]) -> None:
    """Set custom room existence validator hook."""
    global _room_validator
    _room_validator = func


def set_membership_validator(func: Optional[Callable[[str, str], bool]]) -> None:
    """Set custom room membership validator hook."""
    global _membership_validator
    _membership_validator = func


def decode_token_payload(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT access token using configured secret and algorithm.

    Raises:
        JWTError or ValueError on invalid/expired tokens.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if "sub" not in payload and "user_id" not in payload:
        raise ValueError("Missing subject identifier in token payload")
    return payload


async def validate_websocket_auth(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str],
) -> Optional[Dict[str, Any]]:
    """
    Perform pre-accept security validation:
    1. JWT token validation (close with 4001 if invalid/missing).
    2. Room existence verification (close with 4004 if room not found).
    3. Room membership check (close with 4003 if not a member).

    Returns:
        User payload dict if valid, or None if connection was closed.
    """
    # 1. JWT Token Check
    if not token or not token.strip():
        logger.warning(f"WebSocket connection rejected: Missing token for room '{room_id}'")
        await websocket.close(code=4001, reason="Unauthorized: Missing token")
        return None

    try:
        user_info = decode_token_payload(token.strip())
    except (JWTError, ValueError, Exception) as e:
        logger.warning(f"WebSocket connection rejected: Invalid JWT token ({e}) for room '{room_id}'")
        await websocket.close(code=4001, reason="Unauthorized: Invalid token")
        return None

    user_id = str(user_info.get("sub") or user_info.get("user_id"))

    # 2. Room Existence Check (if validator registered)
    if _room_validator is not None:
        try:
            room_exists = _room_validator(room_id)
            if not room_exists:
                logger.warning(f"WebSocket connection rejected: Room '{room_id}' not found")
                await websocket.close(code=4004, reason="Room not found")
                return None
        except Exception as e:
            logger.error(f"Error checking room existence: {e}")
            await websocket.close(code=4004, reason="Room not found")
            return None

    # 3. Room Membership Check (if validator registered)
    if _membership_validator is not None:
        try:
            is_member = _membership_validator(room_id, user_id)
            if not is_member:
                logger.warning(f"WebSocket connection rejected: User '{user_id}' is not member of room '{room_id}'")
                await websocket.close(code=4003, reason="Forbidden: Not a room member")
                return None
        except Exception as e:
            logger.error(f"Error checking room membership: {e}")
            await websocket.close(code=4003, reason="Forbidden: Not a room member")
            return None

    return user_info


@router.websocket("/{room_id}")
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str] = Query(None, description="JWT access token"),
) -> None:
    """
    WebSocket endpoint for real-time room messaging.

    Connection flow (docs/websocket-contract.md):
    1. Validate JWT token -> close 4001 if invalid.
    2. Validate room existence -> close 4004 if not found.
    3. Validate room membership -> close 4003 if not member.
    4. Accept connection and register in ConnectionManager.
    5. Broadcast JOIN event to all room members.
    6. Message loop (receive -> parse -> process).
    7. On disconnect -> unregister and broadcast LEAVE event.
    """
    r_id = str(room_id)

    # ── Pre-Accept Security Verification ──────────────────────────────────────
    user_info = await validate_websocket_auth(
        websocket=websocket,
        room_id=r_id,
        token=token,
    )
    if user_info is None:
        return

    user_id = str(user_info.get("sub") or user_info.get("user_id"))
    username = str(user_info.get("username") or user_info.get("name") or user_id[:8])
    preferred_language = str(user_info.get("preferred_language") or "en")

    # ── Accept & Register Connection ──────────────────────────────────────────
    await manager.connect(
        websocket=websocket,
        room_id=r_id,
        user_id=user_id,
        username=username,
        preferred_language=preferred_language,
        accept_connection=True,
    )

    # ── Broadcast JOIN Event ──────────────────────────────────────────────────
    join_event = {
        "type": WSMessageType.JOIN.value,
        "payload": {
            "user_id": user_id,
            "username": username,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "room_id": r_id,
    }
    await manager.broadcast_to_room(r_id, join_event)

    # ── Message Processing Loop ───────────────────────────────────────────────
    try:
        while True:
            raw_text = await websocket.receive_text()
            msg_dict, err_dict = parse_and_validate_message(raw_text)

            if err_dict:
                # Send error envelope back to the sender
                await manager.send_to_connection(websocket, err_dict)
                continue

            msg_type = msg_dict.get("type")
            payload = msg_dict.get("payload", {})

            if msg_type == WSMessageType.HEARTBEAT.value:
                manager.record_heartbeat(r_id, user_id)
                continue

            elif msg_type == WSMessageType.TYPING.value:
                # Broadcast typing indicator to all OTHER members in room
                typing_event = {
                    "type": WSMessageType.TYPING.value,
                    "payload": {
                        "user_id": user_id,
                        "username": username,
                        "is_typing": bool(payload.get("is_typing", False)),
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "room_id": r_id,
                }
                await manager.broadcast_to_room(
                    r_id,
                    typing_event,
                    exclude_connection=websocket,
                )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally for user '{username}' in room '{r_id}'")
    except Exception as e:
        logger.warning(f"WebSocket connection error for user '{username}' in room '{r_id}': {e}")
    finally:
        # ── Cleanup & Broadcast LEAVE Event ───────────────────────────────────
        await manager.disconnect(
            websocket=websocket,
            room_id=r_id,
            user_id=user_id,
            username=username,
        )
        leave_event = {
            "type": WSMessageType.LEAVE.value,
            "payload": {
                "user_id": user_id,
                "username": username,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "room_id": r_id,
        }
        await manager.broadcast_to_room(r_id, leave_event)
