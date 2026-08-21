# حالات النظام وتدفق البيانات (SYSTEM_STATES.md)

توضح هذه الوثيقة دورة حياة العمليات الأساسية داخل نظام **LinguaChat**، وحالات الاتصال، وتدفق البيانات بين مختلف المكونات.

---

## 1. دورة حياة المستخدم والمصادقة (Auth Lifecycle)

```text
[ Unauthenticated Client ]
        │
        ├── POST /api/v1/auth/register ────► Create User in DB + Hash Password
        │                                         │
        │                                         ▼ (201 Created)
        ├── POST /api/v1/auth/login ───────► Verify Password + Generate JWT
        │                                         │
        ▼                                         ▼ (200 OK + access_token)
[ Authenticated Client ] ◄──────────────── Save Token in localStorage
        │
        ├── Injects Authorization: Bearer <token> in REST Requests
        └── Passes ?token=<access_token> in WebSocket Handshake
```

---

## 2. دورة حياة اتصال الويب سوكت (WebSocket Connection Lifecycle)

```text
[ Client initiates WS Connection: ws://localhost:8000/ws/{room_id}?token=... ]
        │
        ▼
[ Server Pre-Accept Security Checks ]
        ├── 1. Validate JWT Token:
        │      ├── Missing / Expired / Invalid ──► Close WS (Code 4001: Unauthorized)
        │      └── Valid ────────────────────────► Extract user_id & preferred_language
        │
        ├── 2. Check Room Existence in DB:
        │      └── Room not found ───────────────► Close WS (Code 4004: Room Not Found)
        │
        └── 3. Check Room Membership in DB:
               └── User not a member ────────────► Close WS (Code 4003: Forbidden)
        │
        ▼ (All Checks Passed)
[ Accept Connection: websocket.accept() ]
        │
        ├── Register in ConnectionManager: manager.connect(room_id, user_id, user_data)
        ├── Broadcast JOIN event to all room members
        │
        ▼
[ Active Connection State ] ◄─────────────────────────────────┐
        │                                                     │
        ├── Client sends HEARTBEAT every 30s ─────────────────┤
        │   └── Server updates last_heartbeat timestamp       │
        │                                                     │
        ├── Client sends TYPING {is_typing: bool} ────────────┤
        │   └── Server broadcasts TYPING to other members     │
        │                                                     │
        ├── Client sends TEXT_MESSAGE {text, original_lang} ──┤
        │   └── (Message Processing Flow - see Section 3)     │
        │                                                     │
        ├── Inactivity Check: No message/heartbeat for 90s ───┴──► Server Closes WS
        │
        ▼
[ Disconnect Event ] (User closes tab, network drops, or timeout)
        │
        ├── manager.disconnect(room_id, user_id)
        └── Broadcast LEAVE event to remaining room members
```

---

## 3. تدفق معالجة وترجمة وحفظ الرسائل (Message Translation & Persistence Flow)

```text
[ Sender Client sends TEXT_MESSAGE ]
        │
        ▼
[ WebSocket Router validates payload (<= 4096 bytes) ]
        │
        ├── Save Original Message to DB: messages_service.create_message()
        │
        ▼
[ For Each Connected Recipient in the Room (Parallel Execution) ]
        │
        ├── Determine Target Language: recipient.preferred_language
        │
        ├── Call Translation Service: translate_message(text, source_lang, target_lang)
        │       │
        │       ├── Case 1: source_lang == target_lang
        │       │     └── Return immediately: source_used="identity", confidence=1.0
        │       │
        │       ├── Case 2: Cache Hit
        │       │     └── Return cached translation: source_used="cache"
        │       │
        │       ├── Case 3: Primary Provider (LibreTranslate)
        │       │     └── Success ──► Cache result & return: source_used="libretranslate"
        │       │
        │       ├── Case 4: Fallback Provider (Google)
        │       │     └── Success ──► Cache result & return: source_used="google"
        │       │
        │       └── Case 5: All Providers Failed
        │             └── Fallback to original text + Send ERROR notification
        │
        ├── Save Translation to DB: messages_service.save_translation()
        │
        ▼
[ Deliver TEXT_MESSAGE to Recipient WebSocket ]
  Payload includes: message_id, sender_id, sender_username, original_text,
                    original_language, translated_text, target_language, translation_source
```
