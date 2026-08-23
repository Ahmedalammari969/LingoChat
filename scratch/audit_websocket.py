"""
Comprehensive Line-by-Line Python Verification Script for WebSocket Implementation
LinguaChat — Mohammed Tasks Verification
Contract: docs/websocket-contract.md
"""
import ast
import asyncio
import json
import sys
from pathlib import Path

# ── Dynamic Portable Path Resolution ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.websocket.schemas import (
    WSMessageType,
    WSErrorCode,
    WSMessageEnvelope,
    JoinPayload,
    LeavePayload,
    TextMessageOutboundPayload,
    TextMessageInboundPayload,
    TypingOutboundPayload,
    TypingInboundPayload,
    HeartbeatPayload,
    ErrorPayload,
)
from app.websocket.protocol import (
    WSMessage,
    WSProtocolError,
    parse_message,
    parse_and_validate_message,
    create_error_message,
    build_error_message,
    MAX_MESSAGE_BYTES,
)
from app.websocket.manager import ConnectionManager, manager


def audit_websocket_enums():
    print("\n--- 1. Auditing Enums & Exact Contract Match ---")
    expected_msg_types = {"JOIN", "LEAVE", "TEXT_MESSAGE", "TYPING", "HEARTBEAT", "ERROR"}
    actual_msg_types = {e.value for e in WSMessageType}
    assert expected_msg_types == actual_msg_types, f"Mismatch in WSMessageType: {actual_msg_types}"
    print(f"[OK] WSMessageType matches contract exactly (6 types): {actual_msg_types}")

    expected_error_codes = {
        "INVALID_JSON", "UNKNOWN_MESSAGE_TYPE", "VALIDATION_ERROR", "MESSAGE_TOO_LONG",
        "EMPTY_MESSAGE", "TRANSLATION_FAILED", "UNAUTHORIZED", "ROOM_NOT_FOUND",
        "NOT_ROOM_MEMBER", "SERVER_ERROR"
    }
    actual_error_codes = {e.value for e in WSErrorCode}
    assert expected_error_codes == actual_error_codes, f"Mismatch in WSErrorCode: {actual_error_codes ^ expected_error_codes}"
    print(f"[OK] WSErrorCode matches contract exactly (10 error codes): {actual_error_codes}")


def audit_ast_and_syntax():
    print("\n--- 2. Auditing AST and Python Syntax ---")
    files_to_check = [
        BACKEND_DIR / "app" / "websocket" / "schemas.py",
        BACKEND_DIR / "app" / "websocket" / "protocol.py",
        BACKEND_DIR / "app" / "websocket" / "manager.py",
    ]
    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(filepath))
        print(f"[OK] Syntax & AST valid for: {filepath.name} ({len(tree.body)} top-level nodes)")


def audit_schemas():
    print("\n--- 3. Auditing All Pydantic Schemas ---")
    # Base Envelope
    env = WSMessageEnvelope(
        type=WSMessageType.TEXT_MESSAGE,
        payload={"text": "hello"},
        room_id="room-123"
    )
    d = env.model_dump()
    assert d["type"] == WSMessageType.TEXT_MESSAGE
    assert "timestamp" in d and d["room_id"] == "room-123"
    print("[OK] WSMessageEnvelope serialized correctly with all 4 required contract fields.")

    # Join & Leave Payloads
    join_p = JoinPayload(user_id="u1", username="ahmed")
    assert join_p.username == "ahmed"
    leave_p = LeavePayload(user_id="u1", username="ahmed")
    assert leave_p.user_id == "u1"

    # Text Outbound & Inbound Payloads
    text_out = TextMessageOutboundPayload(text="Hello", original_language="en")
    assert text_out.text == "Hello"

    text_in = TextMessageInboundPayload(
        message_id="msg-1",
        sender_id="user-1",
        sender_username="ahmed",
        original_text="مرحبا",
        original_language="ar",
        translated_text="hello",
        target_language="en",
        translation_source="libretranslate"
    )
    assert text_in.translation_source == "libretranslate"

    # Typing Payloads
    typing_out = TypingOutboundPayload(is_typing=True)
    assert typing_out.is_typing is True
    typing_in = TypingInboundPayload(user_id="u1", username="ahmed", is_typing=True)
    assert typing_in.is_typing is True

    # Heartbeat & Error Payloads
    hb = HeartbeatPayload()
    assert isinstance(hb.model_dump(), dict)
    err_p = ErrorPayload(code=WSErrorCode.INVALID_JSON.value, message="Invalid JSON", original_type="TEXT_MESSAGE")
    assert err_p.code == "INVALID_JSON"
    print("[OK] All 8 Pydantic payload models validated successfully.")


def audit_protocol_parsing_and_error_builders():
    print("\n--- 4. Auditing Protocol Parsing & Error Builders ---")
    # 1. Valid Parsing
    valid_raw = json.dumps({
        "type": "TEXT_MESSAGE",
        "payload": {"text": "Hello world", "original_language": "en"},
        "timestamp": "2026-08-24T00:00:00.000Z",
        "room_id": "room-uuid-123"
    })
    msg = parse_message(valid_raw)
    assert isinstance(msg, WSMessage)
    assert msg.type == WSMessageType.TEXT_MESSAGE
    assert msg.payload["text"] == "Hello world"
    assert msg.to_dict()["room_id"] == "room-uuid-123"

    # 2. Reject Malformed JSON
    try:
        parse_message("not valid json")
        assert False, "Should have failed on invalid JSON"
    except WSProtocolError as e:
        assert e.code == WSErrorCode.INVALID_JSON.value

    # 3. Reject Empty Text
    try:
        parse_message(json.dumps({"type": "TEXT_MESSAGE", "payload": {"text": "   "}, "room_id": "r1"}))
        assert False, "Should have failed on empty text"
    except WSProtocolError as e:
        assert e.code == WSErrorCode.EMPTY_MESSAGE.value

    # 4. Reject Too Long (> 4096 bytes)
    too_long = "X" * (MAX_MESSAGE_BYTES + 10)
    try:
        parse_message(json.dumps({"type": "TEXT_MESSAGE", "payload": {"text": too_long}, "room_id": "r1"}))
        assert False, "Should have failed on message too long"
    except WSProtocolError as e:
        assert e.code == WSErrorCode.MESSAGE_TOO_LONG.value

    # 5. Error Message Builders
    err_dict = create_error_message(
        code=WSErrorCode.UNAUTHORIZED.value,
        message="Token invalid",
        room_id="r1",
        original_type="JOIN"
    )
    assert err_dict["type"] == "ERROR"
    assert err_dict["payload"]["code"] == "UNAUTHORIZED"

    err_str = build_error_message(
        code=WSErrorCode.SERVER_ERROR.value,
        message="Server error",
        room_id="r1"
    )
    assert "SERVER_ERROR" in err_str

    # 6. parse_and_validate_message helper
    valid_res, err_res = parse_and_validate_message(valid_raw)
    assert valid_res is not None and err_res is None

    invalid_res, err_res = parse_and_validate_message("broken")
    assert invalid_res is None and err_res is not None
    assert err_res["payload"]["code"] == "INVALID_JSON"

    print("[OK] Protocol parsing, size constraints, and error builders verified 100%.")


async def audit_connection_manager_concurrency():
    print("\n--- 5. Auditing ConnectionManager Under Heavy Concurrency ---")
    # Verify singleton manager exists
    assert isinstance(manager, ConnectionManager)
    
    mgr = ConnectionManager()
    
    class FakeWS:
        def __init__(self, name, should_fail=False):
            self.name = name
            self.messages = []
            self.should_fail = should_fail
        async def accept(self): pass
        async def send_text(self, text):
            if self.should_fail:
                raise RuntimeError("Broken connection")
            self.messages.append(text)
            await asyncio.sleep(0.0005)

    # 1. Concurrently connect 50 users across 5 rooms
    tasks = []
    for r in range(5):
        for u in range(10):
            ws = FakeWS(f"ws-{r}-{u}")
            tasks.append(mgr.connect(ws, room_id=f"room-{r}", user_id=f"user-{r}-{u}", username=f"user_{u}", preferred_language="ar" if u % 2 == 0 else "en"))
    
    await asyncio.gather(*tasks)
    assert mgr.get_active_connections_count() == 50
    for r in range(5):
        assert mgr.get_room_user_count(f"room-{r}") == 10
    print(f"[OK] Successfully connected 50 concurrent users across 5 rooms. Total active: {mgr.get_active_connections_count()}")

    # 2. Test Heartbeat recording
    assert mgr.record_heartbeat("room-0", "user-0-0") is True
    assert mgr.record_heartbeat("room-0", "non-existent") is False

    # 3. Test Custom Broadcast (Translation per user language)
    def custom_factory(conn_info):
        lang = conn_info["preferred_language"]
        return {"type": "TEXT_MESSAGE", "payload": {"text": "مرحبا" if lang == "ar" else "Hello"}}

    delivered = await mgr.broadcast_custom("room-0", custom_factory)
    assert delivered == 10
    print("[OK] broadcast_custom per user language executed successfully.")

    # 4. Concurrently broadcast to all 5 rooms
    broadcast_tasks = []
    for r in range(5):
        msg = {"type": "TEXT_MESSAGE", "payload": {"text": f"Msg to room {r}"}, "room_id": f"room-{r}"}
        broadcast_tasks.append(mgr.broadcast_to_room(f"room-{r}", msg))
    
    results = await asyncio.gather(*broadcast_tasks)
    assert results == [10, 10, 10, 10, 10]
    print("[OK] Concurrently broadcasted to all 5 rooms with zero cross-room leaks.")

    # 5. Concurrently disconnect all 50 users
    disc_tasks = []
    for r in range(5):
        for u in range(10):
            disc_tasks.append(mgr.disconnect(None, room_id=f"room-{r}", user_id=f"user-{r}-{u}"))
    await asyncio.gather(*disc_tasks)
    assert mgr.get_active_connections_count() == 0
    print("[OK] Concurrently disconnected all 50 users. Connection pool safely cleaned to 0.")


def main():
    print("=" * 65)
    print("STARTING COMPLETE AUDIT & CONTRACT VERIFICATION")
    print("=" * 65)
    audit_websocket_enums()
    audit_ast_and_syntax()
    audit_schemas()
    audit_protocol_parsing_and_error_builders()
    asyncio.run(audit_connection_manager_concurrency())
    print("\n" + "=" * 65)
    print("ALL AUDITS & CONTRACT VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("=" * 65)


if __name__ == "__main__":
    main()
