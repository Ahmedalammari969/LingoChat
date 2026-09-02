from __future__ import annotations
"""
LinguaChat — WebSocket Router

Endpoint: ws://localhost:8000/ws/{room_id}?token=<access_token>
Implementation: Mohammed Al-Daees — TASK-04-MOHAMMED
Contract: docs/websocket-contract.md § Message Types & Translation Flow
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from app.core.config import settings
from app.core.errors import TranslationError
from app.translation import service as translation_service
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
_room_validator: Optional[Callable[[str], bool]] = None
_membership_validator: Optional[Callable[[str, str], bool]] = None
_message_persister: Optional[Callable[..., Any]] = None


def set_room_validator(func: Optional[Callable[[str], bool]]) -> None:
    """Set custom room existence validator hook."""
    global _room_validator
    _room_validator = func


def set_membership_validator(func: Optional[Callable[[str, str], bool]]) -> None:
    """Set custom room membership validator hook."""
    global _membership_validator
    _membership_validator = func


def set_message_persister(func: Optional[Callable[..., Any]]) -> None:
    """Set custom database persistence hook."""
    global _message_persister
    _message_persister = func


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
    Perform security validation after accepting the WebSocket connection.
    
    IMPORTANT: We must accept() first, then validate, then close with error code
    if invalid. Calling close() before accept() causes browsers on external devices
    to hang in "connecting" state indefinitely.
    
    Returns:
        User payload dict if valid, or None if connection was closed.
    """
    # Accept the connection first — this is required before we can send close frames
    try:
        await websocket.accept()
    except Exception as e:
        logger.warning(f"WebSocket accept failed for room '{room_id}': {e}")
        return None

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



async def _translate_and_send_to_recipient(
    recipient_conn: Dict[str, Any],
    room_id: str,
    message_id: str,
    sender_id: str,
    sender_username: str,
    original_text: str,
    source_lang: str,
    now_iso: str,
) -> bool:
    """
    Translate text into recipient's preferred language and send the TEXT_MESSAGE envelope.
    """
    ws: WebSocket = recipient_conn["ws"]
    target_lang = str(recipient_conn.get("preferred_language") or "en")

    try:
        res = await translation_service.translate_message(
            text=original_text,
            source_lang=source_lang,
            target_lang=target_lang,
        )
        translated_text = res.get("translated_text", original_text)
        translation_source = res.get("source_used", "identity")
    except (TranslationError, Exception) as ex:
        logger.warning(f"Translation failed for recipient {recipient_conn.get('username')}: {ex}")
        translated_text = original_text
        translation_source = "identity" if source_lang == target_lang else "libretranslate"

    inbound_message = {
        "type": WSMessageType.TEXT_MESSAGE.value,
        "payload": {
            "message_id": message_id,
            "sender_id": sender_id,
            "sender_username": sender_username,
            "original_text": original_text,
            "original_language": source_lang if source_lang != "auto" else "en",
            "translated_text": translated_text,
            "target_language": target_lang,
            "translation_source": translation_source,
        },
        "timestamp": now_iso,
        "room_id": room_id,
    }

    return await manager.send_to_connection(ws, inbound_message)


@router.websocket("/{room_id}")
@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str] = Query(None, description="JWT access token"),
) -> None:
    """
    WebSocket endpoint for real-time room messaging and translation.

    Connection flow (docs/websocket-contract.md):
    1. Pre-accept security validation (JWT 4001, Room 4004, Member 4003).
    2. Accept connection and register in ConnectionManager.
    3. Broadcast JOIN event to all room members.
    4. Message loop:
       - HEARTBEAT -> record last_heartbeat
       - TYPING -> broadcast to other room members
       - TEXT_MESSAGE -> translate per recipient's preferred_language & broadcast
    5. On disconnect -> unregister and broadcast LEAVE event.
    """
    r_id = str(room_id)

    # ── 1. Pre-Accept Security Verification ──────────────────────────────────
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

    # ── 2. Register Connection (already accepted in validate_websocket_auth) ──
    await manager.connect(
        websocket=websocket,
        room_id=r_id,
        user_id=user_id,
        username=username,
        preferred_language=preferred_language,
        accept_connection=False,
    )

    # ── 3. Broadcast JOIN Event ──────────────────────────────────────────────
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

    # ── 4. Message Processing Loop ───────────────────────────────────────────
    try:
        while True:
            raw_text = await websocket.receive_text()
            msg_dict, err_dict = parse_and_validate_message(raw_text)

            if err_dict:
                # Deliver standard ERROR envelope to the sender without dropping connection
                await manager.send_to_connection(websocket, err_dict)
                continue

            msg_type = msg_dict.get("type")
            payload = msg_dict.get("payload", {})
            now_iso = datetime.now(timezone.utc).isoformat()

            # ── A. HEARTBEAT ─────────────────────────────────────────────────
            if msg_type == WSMessageType.HEARTBEAT.value:
                manager.record_heartbeat(r_id, user_id)
                continue

            # ── B. TYPING ────────────────────────────────────────────────────
            elif msg_type == WSMessageType.TYPING.value:
                typing_event = {
                    "type": WSMessageType.TYPING.value,
                    "payload": {
                        "user_id": user_id,
                        "username": username,
                        "is_typing": bool(payload.get("is_typing", False)),
                    },
                    "timestamp": now_iso,
                    "room_id": r_id,
                }
                await manager.broadcast_to_room(
                    r_id,
                    typing_event,
                    exclude_connection=websocket,
                )

            # ── C. TEXT_MESSAGE (Real-Time Translation Pipeline) ─────────────
            elif msg_type == WSMessageType.TEXT_MESSAGE.value:
                text_content = str(payload.get("text", "")).strip()
                orig_lang = payload.get("original_language") or "auto"
                msg_id = str(uuid.uuid4())

                # Optional Persistence hook
                if _message_persister is not None:
                    try:
                        await _message_persister(
                            room_id=r_id,
                            sender_id=user_id,
                            text=text_content,
                            original_language=orig_lang,
                            message_id=msg_id,
                        )
                    except Exception as pe:
                        logger.error(f"Error persisting message: {pe}")

                # Snapshot active room connections
                room_connections = manager._rooms.get(r_id, {})
                if room_connections:
                    recipients = list(room_connections.values())
                    # Translate and send concurrently to all room members
                    tasks = [
                        _translate_and_send_to_recipient(
                            recipient_conn=recipient,
                            room_id=r_id,
                            message_id=msg_id,
                            sender_id=user_id,
                            sender_username=username,
                            original_text=text_content,
                            source_lang=orig_lang,
                            now_iso=now_iso,
                        )
                        for recipient in recipients
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)

            # ── D. Live Stream & WebRTC Signaling Events ─────────────────────
            elif msg_type in {
                WSMessageType.LIVE_START.value,
                WSMessageType.LIVE_STOP.value,
                WSMessageType.LIVE_REQUEST_JOIN.value,
                WSMessageType.LIVE_ACCEPT_GUEST.value,
                WSMessageType.LIVE_REJECT_GUEST.value,
                WSMessageType.LIVE_LEAVE_GUEST.value,
                WSMessageType.RTC_OFFER.value,
                WSMessageType.RTC_ANSWER.value,
                WSMessageType.RTC_ICE_CANDIDATE.value,
            }:
                live_event = {
                    "type": msg_type,
                    "payload": {
                        **payload,
                        "sender_id": user_id,
                        "sender_username": username,
                    },
                    "timestamp": now_iso,
                    "room_id": r_id,
                }
                target_user = payload.get("target_user_id") or payload.get("target_user")
                if target_user:
                    room_connections = manager._rooms.get(r_id, {})
                    t_str = str(target_user).replace("-", "").lower()
                    target_conn = None
                    for u_k, u_v in room_connections.items():
                        if u_k == str(target_user) or str(u_k).replace("-", "").lower() == t_str:
                            target_conn = u_v
                            break
                    target_ws = target_conn.get("ws") or target_conn.get("websocket") if target_conn else None
                    if target_ws:
                        await manager.send_to_connection(target_ws, live_event)
                    else:
                        # Fallback to broadcast if target connection was not found directly
                        await manager.broadcast_to_room(
                            r_id,
                            live_event,
                            exclude_connection=websocket if msg_type == WSMessageType.LIVE_REQUEST_JOIN.value else None,
                        )
                else:
                    await manager.broadcast_to_room(
                        r_id,
                        live_event,
                        exclude_connection=websocket if msg_type == WSMessageType.LIVE_REQUEST_JOIN.value else None,
                    )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally for user '{username}' in room '{r_id}'")
    except Exception as e:
        logger.warning(f"WebSocket connection error for user '{username}' in room '{r_id}': {e}")
    finally:
        # ── 5. Cleanup & Broadcast LEAVE Event ───────────────────────────────
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
