# عقد واجهات برمجة التطبيقات (API_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا (Frozen Contract).  
> يمنع تغيير مسارات الـ Endpoints، أو أسماء الحقول، أو رموز الاستجابة، أو صيغة الأخطاء.

---

## 1. القواعد العامة (General Rules)

- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **Authentication**: `Authorization: Bearer <access_token>`
- **صيغة الأخطاء المعيارية (Error Response Envelope)**:
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

## 2. مسارات المصادقة والمستخدمين (Authentication)

### 1. `POST /api/v1/auth/register` (تسجيل مستخدم جديد)
- **Auth**: None (Public)
- **Request Body**:
  ```json
  {
    "username": "string (3-50 chars, alphanumeric + _)",
    "password": "string (min 8 chars)",
    "preferred_language": "string (ISO 639-1 code, e.g. 'ar', 'en', 'fr')"
  }
  ```
- **Responses**:
  - `201 Created`:
    ```json
    {
      "id": "uuid",
      "username": "string",
      "preferred_language": "string",
      "created_at": "ISO8601 UTC"
    }
    ```
  - `400 Bad Request`: `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}`
  - `409 Conflict`: `{"error": {"code": "USERNAME_ALREADY_EXISTS", "message": "Username already taken"}}`
  - `422 Unprocessable Entity`: validation errors.

### 2. `POST /api/v1/auth/login` (تسجيل الدخول وإصدار التوكن)
- **Auth**: None (Public)
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access_token": "string (JWT)",
      "token_type": "bearer",
      "expires_in": 3600
    }
    ```
  - `400 Bad Request`: `{"error": {"code": "VALIDATION_ERROR", "message": "..."}}`
  - `401 Unauthorized`: `{"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"}}`

---

## 3. مسارات إدارة الغرف (Rooms)

### 3. `POST /api/v1/rooms` (إنشاء غرفة جديدة)
- **Auth**: Bearer JWT Required
- **Request Body**:
  ```json
  {
    "name": "string (1-100 chars)"
  }
  ```
- **Responses**:
  - `201 Created`: (يضاف منشئ الغرفة تلقائياً كعضو فيها)
    ```json
    {
      "id": "uuid",
      "name": "string",
      "invitation_link": "string (/rooms/{id}/join)",
      "created_by": "uuid",
      "created_at": "ISO8601 UTC"
    }
    ```
  - `401 Unauthorized`
  - `422 Unprocessable Entity`

### 4. `GET /api/v1/rooms` (استعراض قائمة الغرف)
- **Auth**: Bearer JWT Required
- **Query Params**: `limit=20` (default 20, max 100), `offset=0`
- **Responses**:
  - `200 OK`:
    ```json
    {
      "rooms": [
        {
          "id": "uuid",
          "name": "string",
          "member_count": 0,
          "created_at": "ISO8601 UTC"
        }
      ],
      "total": 0,
      "limit": 20,
      "offset": 0
    }
    ```
  - `401 Unauthorized`

### 5. `POST /api/v1/rooms/{room_id}/join` (الانضمام لغرفة)
- **Auth**: Bearer JWT Required
- **Path Params**: `room_id` (UUID)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "room_id": "uuid",
      "user_id": "uuid",
      "joined_at": "ISO8601 UTC"
    }
    ```
  - `401 Unauthorized`
  - `404 Not Found`: `{"error": {"code": "ROOM_NOT_FOUND", "message": "Room not found"}}`
  - `409 Conflict`: `{"error": {"code": "ALREADY_IN_ROOM", "message": "User is already a member of this room"}}`

---

## 4. مسارات الرسائل والتاريخ (Messages)

### 6. `GET /api/v1/rooms/{room_id}/messages` (استرجاع تاريخ الرسائل المترجمة)
- **Auth**: Bearer JWT Required (يجب أن يكون المستخدم عضواً في الغرفة)
- **Path Params**: `room_id` (UUID)
- **Query Params**: `limit=50` (default 50, max 200), `before=ISO8601` (optional timestamp cursor)
- **Responses**:
  - `200 OK`: (ترجع الرسائل مترجمة للغة المستخدم المفضلة مع النص الأصلي)
    ```json
    {
      "messages": [
        {
          "id": "uuid",
          "room_id": "uuid",
          "sender_id": "uuid",
          "sender_username": "string",
          "original_text": "string",
          "original_language": "string",
          "translated_text": "string",
          "target_language": "string",
          "sent_at": "ISO8601 UTC"
        }
      ],
      "has_more": false
    }
    ```
  - `401 Unauthorized`
  - `403 Forbidden`: `{"error": {"code": "FORBIDDEN", "message": "User is not a member of this room"}}`
  - `404 Not Found`: `{"error": {"code": "ROOM_NOT_FOUND", "message": "Room not found"}}`

---

## 5. مسارات لوحة التحكم (Dashboard)

### 7. `GET /api/v1/dashboard/stats` (إحصائيات النظام)
- **Auth**: Bearer JWT Required
- **Responses**:
  - `200 OK`:
    ```json
    {
      "total_users": 0,
      "total_rooms": 0,
      "total_messages": 0,
      "total_translations": 0,
      "active_connections": 0
    }
    ```
  - `401 Unauthorized`

---

## 6. فحص الصحة (Health Check)

### 8. `GET /health`
- **Auth**: None
- **Responses**: `200 OK` -> `{"status": "healthy"}`
