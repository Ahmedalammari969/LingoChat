# عقد بروتوكول الويب سوكت (WEBSOCKET_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا (Frozen Contract).  
> يسمح فقط بالأنواع الستة المعتمدة للرسائل. يمنع تعديل هيكل الغلاف أو أكواد إغلاق الاتصال.

---

## 1. نقطة الاتصال والمصادقة (Endpoint & Handshake)

- **URL**: `ws://localhost:8000/ws/{room_id}?token=<access_token>`
- **Close Codes**:
  - `4001`: غير مصرح (فشل مصادقة JWT).
  - `4003`: ممنوع (المستخدم ليس عضواً في الغرفة).
  - `4004`: الغرفة غير موجودة.
  - `1000`: إغلاق طبيعي.

---

## 2. هيكل غلاف الرسالة الأساسي (Message Envelope)

جميع رسائل الويب سوكت تلتزم بالحقول الأربعة الإلزامية التالية:

```json
{
  "type": "JOIN | LEAVE | TEXT_MESSAGE | TYPING | HEARTBEAT | ERROR",
  "payload": {},
  "timestamp": "ISO8601 UTC (e.g. 2026-08-13T21:00:00Z)",
  "room_id": "uuid"
}
```

---

## 3. تفاصيل أنواع الرسائل الستة (The 6 Allowed Types)

### 1. `JOIN` (Server -> Clients)
يتم بثه عند نجاح اتصال مستخدم جديد بالغرفة:
```json
{
  "type": "JOIN",
  "payload": {
    "user_id": "uuid",
    "username": "string"
  },
  "timestamp": "ISO8601",
  "room_id": "uuid"
}
```

### 2. `LEAVE` (Server -> Clients)
يتم بثه عند انقطاع أو خروج مستخدم من الغرفة:
```json
{
  "type": "LEAVE",
  "payload": {
    "user_id": "uuid",
    "username": "string"
  },
  "timestamp": "ISO8601",
  "room_id": "uuid"
}
```

### 3. `TEXT_MESSAGE`
- **من العميل إلى الخادم (Client -> Server)**:
  ```json
  {
    "type": "TEXT_MESSAGE",
    "payload": {
      "text": "string (1-4096 bytes)",
      "original_language": "string | null (e.g. 'ar', 'en' or null for auto-detect)"
    },
    "timestamp": "ISO8601",
    "room_id": "uuid"
  }
  ```
- **من الخادم إلى العملاء (Server -> Client - Per Recipient)**:
  ```json
  {
    "type": "TEXT_MESSAGE",
    "payload": {
      "message_id": "uuid",
      "sender_id": "uuid",
      "sender_username": "string",
      "original_text": "string",
      "original_language": "string",
      "translated_text": "string",
      "target_language": "string",
      "translation_source": "libretranslate | google | cache | identity"
    },
    "timestamp": "ISO8601",
    "room_id": "uuid"
  }
  ```

### 4. `TYPING`
- **من العميل إلى الخادم (Client -> Server)**:
  ```json
  {
    "type": "TYPING",
    "payload": {
      "is_typing": true
    },
    "timestamp": "ISO8601",
    "room_id": "uuid"
  }
  ```
- **من الخادم إلى باقي المتواجدين (Server -> Other Clients)**:
  ```json
  {
    "type": "TYPING",
    "payload": {
      "user_id": "uuid",
      "username": "string",
      "is_typing": true
    },
    "timestamp": "ISO8601",
    "room_id": "uuid"
  }
  ```

### 5. `HEARTBEAT` (Client -> Server)
يرسله العميل كل **30 ثانية** للحفاظ على الاتصال، ويفصل الخادم الاتصال بعد **90 ثانية** من الصمت:
```json
{
  "type": "HEARTBEAT",
  "payload": {},
  "timestamp": "ISO8601",
  "room_id": "uuid"
}
```

### 6. `ERROR` (Server -> Client)
يتم إرساله للعميل عند حدوث خطأ دون قطع الاتصال:
```json
{
  "type": "ERROR",
  "payload": {
    "code": "MESSAGE_TOO_LONG | INVALID_JSON | EMPTY_MESSAGE | UNKNOWN_MESSAGE_TYPE | TRANSLATION_FAILED | RATE_LIMITED | SERVER_ERROR",
    "message": "Human-readable error description",
    "original_type": "TEXT_MESSAGE | null"
  },
  "timestamp": "ISO8601",
  "room_id": "uuid"
}
```

---

## 4. القيود الصارمة (Strict Constraints)
- الحد الأقصى لحجم الرسالة: **4096 بايت**.
- ترفض أي رسالة بنوع غير الأنواع الستة بكود `UNKNOWN_MESSAGE_TYPE`.
- عند تطابق لغة المرسل والمستلم يجب أن تكون `translation_source = "identity"`.
