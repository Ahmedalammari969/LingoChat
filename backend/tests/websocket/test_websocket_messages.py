"""
LinguaChat — WebSocket Real-Time Messaging & Translation Tests
Tests for TASK-04-MOHAMMED
Contract: docs/websocket-contract.md § Message Types & Real-Time Translation
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from jose import jwt

from app.main import app
from app.core.config import settings
from app.websocket.router import set_room_validator, set_membership_validator
from app.websocket.schemas import WSMessageType


def generate_test_jwt(user_id: str, username: str = "testuser", preferred_language: str = "en") -> str:
    """Generate a valid JWT token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    payload = {
        "sub": user_id,
        "username": username,
        "preferred_language": preferred_language,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture(autouse=True)
def setup_validators():
    """Allow all rooms and members for tests."""
    set_room_validator(lambda r: True)
    set_membership_validator(lambda r, u: True)
    yield
    set_room_validator(None)
    set_membership_validator(None)


def test_multilingual_chat_message_translation_and_broadcast():
    """
    Test real-time messaging:
    - User 1 (Arabic) sends 'مرحبا'
    - User 2 (English) receives English translated text
    """
    token_ar = generate_test_jwt(user_id="user-ar", username="Ali", preferred_language="ar")
    token_en = generate_test_jwt(user_id="user-en", username="John", preferred_language="en")

    client = TestClient(app)

    with patch("app.translation.service.translate_message", new_callable=AsyncMock) as mock_translate:
        # Mock translate responses
        async def mock_translate_impl(text, source_lang, target_lang):
            if target_lang == "en":
                return {"translated_text": "Hello", "source_used": "libretranslate", "confidence": 0.98}
            elif target_lang == "ar":
                return {"translated_text": "مرحبا", "source_used": "identity", "confidence": 1.0}
            return {"translated_text": text, "source_used": "identity", "confidence": 1.0}

        mock_translate.side_effect = mock_translate_impl

        with client.websocket_connect(f"/ws/room-chat-123?token={token_ar}") as ws_ar:
            # Consume Ali's JOIN
            join1 = json.loads(ws_ar.receive_text())
            assert join1["type"] == WSMessageType.JOIN.value

            with client.websocket_connect(f"/ws/room-chat-123?token={token_en}") as ws_en:
                # Consume John's JOIN from John's connection
                join2_en = json.loads(ws_en.receive_text())
                assert join2_en["type"] == WSMessageType.JOIN.value

                # Consume John's JOIN broadcast from Ali's connection
                join2_ar = json.loads(ws_ar.receive_text())
                assert join2_ar["type"] == WSMessageType.JOIN.value

                # Ali sends an Arabic message
                msg_payload = {
                    "type": "TEXT_MESSAGE",
                    "payload": {
                        "text": "مرحبا",
                        "original_language": "ar"
                    },
                    "room_id": "room-chat-123"
                }
                ws_ar.send_text(json.dumps(msg_payload))

                # Ali receives Arabic version (identity)
                ali_received = json.loads(ws_ar.receive_text())
                assert ali_received["type"] == "TEXT_MESSAGE"
                assert ali_received["payload"]["original_text"] == "مرحبا"
                assert ali_received["payload"]["translated_text"] == "مرحبا"
                assert ali_received["payload"]["target_language"] == "ar"
                assert ali_received["payload"]["sender_username"] == "Ali"

                # John receives English translated version
                john_received = json.loads(ws_en.receive_text())
                assert john_received["type"] == "TEXT_MESSAGE"
                assert john_received["payload"]["original_text"] == "مرحبا"
                assert john_received["payload"]["translated_text"] == "Hello"
                assert john_received["payload"]["target_language"] == "en"
                assert john_received["payload"]["translation_source"] == "libretranslate"
                assert john_received["payload"]["sender_username"] == "Ali"


def test_error_envelope_handling_without_disconnect():
    """Test sending malformed payload returns ERROR envelope and keeps connection alive."""
    token = generate_test_jwt(user_id="user-err", username="ErrorTester")
    client = TestClient(app)

    with client.websocket_connect(f"/ws/room-err-123?token={token}") as ws:
        # Consume JOIN
        ws.receive_text()

        # Send invalid message (empty text)
        ws.send_text(json.dumps({
            "type": "TEXT_MESSAGE",
            "payload": {"text": "   "},
            "room_id": "room-err-123"
        }))

        # Receive ERROR envelope
        err_msg = json.loads(ws.receive_text())
        assert err_msg["type"] == "ERROR"
        assert err_msg["payload"]["code"] == "EMPTY_MESSAGE"

        # Connection is still open, send valid Heartbeat
        ws.send_text(json.dumps({
            "type": "HEARTBEAT",
            "payload": {},
            "room_id": "room-err-123"
        }))
