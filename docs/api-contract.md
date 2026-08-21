# LinguaChat — REST API Contract

> **STATUS: SOURCE OF TRUTH**
> All team members and AI agents MUST NOT deviate from these endpoints.
> Any change requires Team Leader approval (Ahmed Alammari).

---

## Base URL

```
http://localhost:8000/api/v1
```

All endpoints (except `/health`) are prefixed with `/api/v1`.

---

## Authentication

All protected endpoints require a Bearer JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

---

### 1. POST /auth/register

**Description**: Register a new user account.

**Authentication**: None (public)

**Request Body**:
```json
{
  "username": "string",
  "password": "string",
  "preferred_language": "string"
}
```

**Validation Rules**:
- `username`: 3–50 characters, alphanumeric + underscores only, unique
- `password`: minimum 8 characters
- `preferred_language`: valid ISO 639-1 language code (e.g., "ar", "en", "fr")

**Success Response** — `201 Created`:
```json
{
  "id": "uuid",
  "username": "string",
  "preferred_language": "string",
  "created_at": "ISO8601"
}
```

**Error Cases**:

| Status | Code                    | Description                      |
|--------|-------------------------|----------------------------------|
| 400    | VALIDATION_ERROR        | Invalid input fields             |
| 409    | USERNAME_ALREADY_EXISTS | Username is taken                |
| 422    | UNPROCESSABLE_ENTITY    | Malformed request body           |
| 500    | INTERNAL_SERVER_ERROR   | Server-side failure              |

---

### 2. POST /auth/login

**Description**: Authenticate an existing user and receive a JWT token.

**Authentication**: None (public)

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Validation Rules**:
- `username`: required, non-empty string
- `password`: required, non-empty string

**Success Response** — `200 OK`:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Cases**:

| Status | Code                  | Description                          |
|--------|-----------------------|--------------------------------------|
| 401    | INVALID_CREDENTIALS   | Wrong username or password           |
| 422    | UNPROCESSABLE_ENTITY  | Malformed request body               |
| 500    | INTERNAL_SERVER_ERROR | Server-side failure                  |

---

### 3. POST /rooms

**Description**: Create a new chat room. Returns a Room ID and invitation link.

**Authentication**: Required (Bearer JWT)

**Request Body**:
```json
{
  "name": "string"
}
```

**Validation Rules**:
- `name`: 1–100 characters, non-empty

**Success Response** — `201 Created`:
```json
{
  "id": "uuid",
  "name": "string",
  "invitation_link": "string",
  "created_by": "uuid",
  "created_at": "ISO8601"
}
```

**Error Cases**:

| Status | Code                  | Description                          |
|--------|-----------------------|--------------------------------------|
| 400    | VALIDATION_ERROR      | Invalid room name                    |
| 401    | UNAUTHORIZED          | Missing or invalid JWT               |
| 500    | INTERNAL_SERVER_ERROR | Server-side failure                  |

---

### 4. GET /rooms

**Description**: List all rooms (or rooms the user is a member of — to be decided in implementation).

**Authentication**: Required (Bearer JWT)

**Query Parameters** (optional):
- `limit`: integer, default 20, max 100
- `offset`: integer, default 0

**Success Response** — `200 OK`:
```json
{
  "rooms": [
    {
      "id": "uuid",
      "name": "string",
      "member_count": 0,
      "created_at": "ISO8601"
    }
  ],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

**Error Cases**:

| Status | Code                  | Description              |
|--------|-----------------------|--------------------------|
| 401    | UNAUTHORIZED          | Missing or invalid JWT   |
| 500    | INTERNAL_SERVER_ERROR | Server-side failure      |

---

### 5. POST /rooms/{room_id}/join

**Description**: Join an existing room by room ID.

**Authentication**: Required (Bearer JWT)

**Path Parameters**:
- `room_id`: UUID of the room

**Request Body**: None

**Success Response** — `200 OK`:
```json
{
  "room_id": "uuid",
  "user_id": "uuid",
  "joined_at": "ISO8601"
}
```

**Error Cases**:

| Status | Code                      | Description                        |
|--------|---------------------------|------------------------------------|
| 401    | UNAUTHORIZED              | Missing or invalid JWT             |
| 404    | ROOM_NOT_FOUND            | Room does not exist                |
| 409    | ALREADY_IN_ROOM           | User is already a member           |
| 500    | INTERNAL_SERVER_ERROR     | Server-side failure                |

---

### 6. GET /rooms/{room_id}/messages

**Description**: Retrieve message history for a room (paginated).

**Authentication**: Required (Bearer JWT) + must be room member.

**Path Parameters**:
- `room_id`: UUID of the room

**Query Parameters** (optional):
- `limit`: integer, default 50, max 200
- `before`: ISO8601 timestamp — return messages before this time (for cursor pagination)

**Success Response** — `200 OK`:
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
      "sent_at": "ISO8601"
    }
  ],
  "has_more": false
}
```

**Notes**:
- `translated_text` is translated into the requesting user's preferred language.
- `original_text` is always included.

**Error Cases**:

| Status | Code                  | Description                            |
|--------|-----------------------|----------------------------------------|
| 401    | UNAUTHORIZED          | Missing or invalid JWT                 |
| 403    | FORBIDDEN             | User is not a member of this room      |
| 404    | ROOM_NOT_FOUND        | Room does not exist                    |
| 500    | INTERNAL_SERVER_ERROR | Server-side failure                    |

---

### 7. GET /dashboard/stats

**Description**: Retrieve aggregate system statistics.

**Authentication**: Required (Bearer JWT)

**Success Response** — `200 OK`:
```json
{
  "total_users": 0,
  "total_rooms": 0,
  "total_messages": 0,
  "total_translations": 0,
  "active_connections": 0
}
```

**Error Cases**:

| Status | Code                  | Description            |
|--------|-----------------------|------------------------|
| 401    | UNAUTHORIZED          | Missing or invalid JWT |
| 500    | INTERNAL_SERVER_ERROR | Server-side failure    |

---

### 8. GET /health

**Description**: Health check endpoint (no authentication required).

**Authentication**: None

**Success Response** — `200 OK`:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Standard Error Response Format

All errors follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

---

## Rules

- Do NOT create endpoints not listed here without Team Leader approval.
- Do NOT rename these endpoints.
- All timestamps are ISO 8601 UTC format.
- All IDs are UUIDs (v4).
- All responses use `application/json` content type.
