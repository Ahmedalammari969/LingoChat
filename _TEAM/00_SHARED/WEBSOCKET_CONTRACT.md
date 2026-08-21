# عقد بروتوكول الويب سوكت (WEBSOCKET_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا. تقتصر رسائل الويب سوكت على الأنواع الستة المعتمدة فقط.

---

## 1. نقطة الاتصال وأكواد الإغلاق (Endpoint & Close Codes)
- **URL**: `ws://localhost:8000/ws/{room_id}?token=<access_token>`
- **Close Codes**:
  - `4001`: غير مصرح (فشل مصادقة JWT).
  - `4003`: ممنوع (المستخدم ليس عضواً في الغرفة).
  - `4004`: الغرفة غير موجودة.
  - `1000`: إغلاق طبيعي.

---

## 2. الغلاف الموحد والأنواع الستة للرسائل (The 6 Allowed Types)

```json
{
  "type": "JOIN | LEAVE | TEXT_MESSAGE | TYPING | HEARTBEAT | ERROR",
  "payload": {},
  "timestamp": "ISO8601 UTC",
  "room_id": "uuid"
}
```

1. **`JOIN`** (Server -> Clients): `payload: {"user_id": "uuid", "username": "str"}`
2. **`LEAVE`** (Server -> Clients): `payload: {"user_id": "uuid", "username": "str"}`
3. **`TEXT_MESSAGE`**:
   - **Client -> Server**: `payload: {"text": "str (max 4096 bytes)", "original_language": "str | null"}`
   - **Server -> Client**: `payload: {"message_id": "uuid", "sender_id": "uuid", "sender_username": "str", "original_text": "str", "original_language": "str", "translated_text": "str", "target_language": "str", "translation_source": "libretranslate | google | cache | identity"}`
4. **`TYPING`**:
   - **Client -> Server**: `payload: {"is_typing": bool}`
   - **Server -> Other Clients**: `payload: {"user_id": "uuid", "username": "str", "is_typing": bool}`
5. **`HEARTBEAT`** (Client -> Server):
   - يرسل كل **30 ثانية** من العميل، ويفصل الخادم الاتصال بعد **90 ثانية** من الصمت.
   - `payload: {}`
6. **`ERROR`** (Server -> Client):
   - `payload: {"code": "MESSAGE_TOO_LONG | INVALID_JSON | EMPTY_MESSAGE | UNKNOWN_MESSAGE_TYPE | TRANSLATION_FAILED | SERVER_ERROR", "message": "str", "original_type": "str | null"}`
