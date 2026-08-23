"""
LinguaChat — WebSocket Translation Integration Tests
Tests for TASK-04-MOHAMMED & Translation Service Integration
Contract: docs/websocket-contract.md & docs/translation-contract.md
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


def generate_jwt(user_id: str, username: str, preferred_language: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "preferred_language": preferred_language,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture(autouse=True)
def setup_validators():
    set_room_validator(lambda r: True)
    set_membership_validator(lambda r, u: True)
    yield
    set_room_validator(None)
    set_membership_validator(None)


def test_three_way_multilingual_chat_room():
    """
    Test 3 users in the same room with different preferred languages:
    - User A (Arabic)
    - User B (English)
    - User C (French)
    When User B sends "Welcome to LinguaChat", all 3 receive appropriate translations.
    """
    token_ar = generate_jwt("user-ar", "Ahmad", "ar")
    token_en = generate_jwt("user-en", "Bob", "en")
    token_fr = generate_jwt("user-fr", "Claire", "fr")

    client = TestClient(app)

    with patch("app.translation.service.translate_message", new_callable=AsyncMock) as mock_translate:
        async def mock_translate_impl(text, source_lang, target_lang):
            translations = {
                ("en", "ar"): "مرحبا بكم في لينجوا شات",
                ("en", "fr"): "Bienvenue sur LinguaChat",
                ("en", "en"): text,
            }
            res = translations.get((source_lang, target_lang), text)
            source = "identity" if source_lang == target_lang else "libretranslate"
            return {"translated_text": res, "source_used": source, "confidence": 0.95}

        mock_translate.side_effect = mock_translate_impl

        with client.websocket_connect(f"/ws/room-tri?token={token_ar}") as ws_ar:
            ws_ar.receive_text()  # Ahmad JOIN

            with client.websocket_connect(f"/ws/room-tri?token={token_en}") as ws_en:
                ws_en.receive_text()  # Bob JOIN (Bob's view)
                ws_ar.receive_text()  # Bob JOIN (Ahmad's view)

                with client.websocket_connect(f"/ws/room-tri?token={token_fr}") as ws_fr:
                    ws_fr.receive_text()  # Claire JOIN (Claire's view)
                    ws_ar.receive_text()  # Claire JOIN (Ahmad's view)
                    ws_en.receive_text()  # Claire JOIN (Bob's view)

                    # Bob sends English text
                    ws_en.send_text(json.dumps({
                        "type": "TEXT_MESSAGE",
                        "payload": {"text": "Welcome to LinguaChat", "original_language": "en"},
                        "room_id": "room-tri"
                    }))

                    # Bob receives English
                    bob_msg = json.loads(ws_en.receive_text())
                    assert bob_msg["payload"]["translated_text"] == "Welcome to LinguaChat"
                    assert bob_msg["payload"]["translation_source"] == "identity"

                    # Ahmad receives Arabic
                    ahmad_msg = json.loads(ws_ar.receive_text())
                    assert ahmad_msg["payload"]["translated_text"] == "مرحبا بكم في لينجوا شات"
                    assert ahmad_msg["payload"]["target_language"] == "ar"

                    # Claire receives French
                    claire_msg = json.loads(ws_fr.receive_text())
                    assert claire_msg["payload"]["translated_text"] == "Bienvenue sur LinguaChat"
                    assert claire_msg["payload"]["target_language"] == "fr"
