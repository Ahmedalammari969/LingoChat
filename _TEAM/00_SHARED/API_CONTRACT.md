# عقد واجهات برمجة التطبيقات (API_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا. يمنع تعديل المسارات أو أسماء الحقول أو صيغة الأخطاء.

---

## 1. القواعد العامة (General Rules)
- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: `Authorization: Bearer <access_token>`
- **Error Envelope**:
  ```json
  {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "Human-readable description",
      "details": {}
    }
  }
  ```

---

## 2. المسارات الرسمية (Official Endpoints)

1. `POST /api/v1/auth/register` (تسجيل حساب جديد):
   - **Body**: `{"username": "str", "password": "str (min 8)", "preferred_language": "str (ISO 639-1)"}`
   - **201 Created**: `{"id": "uuid", "username": "str", "preferred_language": "str", "created_at": "ISO8601"}`
   - **409 Conflict**: `{"error": {"code": "USERNAME_ALREADY_EXISTS", "message": "..."}}`

2. `POST /api/v1/auth/login` (تسجيل الدخول وإصدار JWT):
   - **Body**: `{"username": "str", "password": "str"}`
   - **200 OK**: `{"access_token": "str", "token_type": "bearer", "expires_in": 3600}`
   - **401 Unauthorized**: `{"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}}`

3. `POST /api/v1/rooms` (إنشاء غرفة جديدة - يتطلب JWT):
   - **Body**: `{"name": "str"}`
   - **201 Created**: `{"id": "uuid", "name": "str", "invitation_link": "str", "created_by": "uuid", "created_at": "ISO8601"}`

4. `GET /api/v1/rooms` (استعراض الغرف - يتطلب JWT):
   - **Query**: `limit=20, offset=0`
   - **200 OK**: `{"rooms": [{"id": "uuid", "name": "str", "member_count": 0, "created_at": "ISO8601"}], "total": 0, "limit": 20, "offset": 0}`

5. `POST /api/v1/rooms/{room_id}/join` (الانضمام لغرفة - يتطلب JWT):
   - **200 OK**: `{"room_id": "uuid", "user_id": "uuid", "joined_at": "ISO8601"}`
   - **404 Not Found**: `{"error": {"code": "ROOM_NOT_FOUND", "message": "..."}}`
   - **409 Conflict**: `{"error": {"code": "ALREADY_IN_ROOM", "message": "..."}}`

6. `GET /api/v1/rooms/{room_id}/messages` (استرجاع تاريخ الرسائل المترجمة - يتطلب JWT وعضوية):
   - **Query**: `limit=50, before=ISO8601`
   - **200 OK**: `{"messages": [{"id": "uuid", "room_id": "uuid", "sender_id": "uuid", "sender_username": "str", "original_text": "str", "original_language": "str", "translated_text": "str", "target_language": "str", "sent_at": "ISO8601"}], "has_more": false}`
   - **403 Forbidden**: `{"error": {"code": "FORBIDDEN", "message": "User is not a member of this room"}}`

7. `GET /api/v1/dashboard/stats` (إحصائيات لوحة التحكم - يتطلب JWT):
   - **200 OK**: `{"total_users": 0, "total_rooms": 0, "total_messages": 0, "total_translations": 0, "active_connections": 0}`

8. `GET /health` (فحص الصحة):
   - **200 OK**: `{"status": "healthy"}`
