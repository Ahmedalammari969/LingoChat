# LinguaChat — WebSocket Contract

> **STATUS: SOURCE OF TRUTH**
> Do NOT change WebSocket message types or formats without Team Leader approval.
> Responsible Engineer: Mohammed Al-Daees

---

## WebSocket Endpoint

```
ws://localhost:8000/ws/{room_id}
```

**Authentication**: JWT token passed as query parameter:
```
ws://localhost:8000/ws/{room_id}?token=<access_token>
```

---

## Connection Lifecycle

```
Client connects to /ws/{room_id}?token=<jwt>
        │
        ▼
Server validates JWT
        │
   INVALID ──► Close with code 4001 (Unauthorized)
        │
   VALID ──►
        │
        ▼
Server validates room membership
        │
   NOT MEMBER ──► Close with code 4003 (Forbidden)
        │
   MEMBER ──►
        │
        ▼
Connection established
Server sends JOIN event to all room members
        │
        ▼
Message exchange (bidirectional)
        │
        ▼
Client disconnects OR server closes
Server sends LEAVE event to remaining members
```

---

## Base Message Format

All WebSocket messages (client → server and server → client) follow this envelope:

```json
{
  "type": "MESSAGE_TYPE",
  "payload": {},
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid-string"
}
```

| Field       | Type   | Required | Description                              |
|-------------|--------|----------|------------------------------------------|
| `type`      | string | Yes      | One of the defined message types below   |
| `payload`   | object | Yes      | Message-specific data (can be `{}`)      |
| `timestamp` | string | Yes      | ISO 8601 UTC timestamp                   |
| `room_id`   | string | Yes      | UUID of the target room                  |

---

## Message Types

### Defined Types (Official)

| Type            | Direction        | Description                        |
|-----------------|------------------|------------------------------------|
| `JOIN`          | Server → Client  | User joined the room               |
| `LEAVE`         | Server → Client  | User left the room                 |
| `TEXT_MESSAGE`  | Client → Server, Server → Client | Chat message      |
| `TYPING`        | Client → Server, Server → Client | Typing indicator  |
| `HEARTBEAT`     | Client → Server  | Keep-alive ping                    |
| `ERROR`         | Server → Client  | Error notification                 |

> **IMPORTANT**: No new message types may be added without Team Leader approval.

---

## Message Type Specifications

---

### JOIN

Sent by **server** to all room members when a user joins.

**Direction**: Server → All Clients in Room

```json
{
  "type": "JOIN",
  "payload": {
    "user_id": "uuid",
    "username": "string"
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

---

### LEAVE

Sent by **server** to all remaining room members when a user disconnects or leaves.

**Direction**: Server → Remaining Clients in Room

```json
{
  "type": "LEAVE",
  "payload": {
    "user_id": "uuid",
    "username": "string"
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

---

### TEXT_MESSAGE

Sent by **client** to server; server translates and broadcasts to each recipient.

**Direction (Outbound — Client → Server)**:
```json
{
  "type": "TEXT_MESSAGE",
  "payload": {
    "text": "string",
    "original_language": "string | null"
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

| Field               | Required | Notes                                     |
|---------------------|----------|-------------------------------------------|
| `text`              | Yes      | The message content                       |
| `original_language` | No       | ISO 639-1 code; auto-detected if omitted  |

**Direction (Inbound — Server → Client)**:
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
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

**Notes**:
- `translated_text` is translated into the receiving user's `preferred_language`.
- If sender's language == receiver's language, `translated_text == original_text` and `translation_source = "identity"`.
- `original_text` is ALWAYS included.

---

### TYPING

Sent by **client** when typing; server broadcasts to other room members.

**Direction (Outbound — Client → Server)**:
```json
{
  "type": "TYPING",
  "payload": {
    "is_typing": true
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

**Direction (Inbound — Server → Other Clients)**:
```json
{
  "type": "TYPING",
  "payload": {
    "user_id": "uuid",
    "username": "string",
    "is_typing": true
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

---

### HEARTBEAT

Sent by **client** every 30 seconds to keep the connection alive.
Server does NOT respond to HEARTBEAT — it only uses it to detect alive connections.

**Direction**: Client → Server only

```json
{
  "type": "HEARTBEAT",
  "payload": {},
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

**Strategy**:
- Client MUST send HEARTBEAT every **30 seconds**.
- Server MUST close connections silent for **90 seconds** (3 missed heartbeats).
- Client MUST attempt reconnection with exponential backoff on disconnect.

---

### ERROR

Sent by **server** to a specific client when an error occurs during message processing.

**Direction**: Server → Client (specific)

```json
{
  "type": "ERROR",
  "payload": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "original_type": "TEXT_MESSAGE"
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "room_id": "uuid"
}
```

**Error Codes**:

| Code                    | Description                                    |
|-------------------------|------------------------------------------------|
| `INVALID_JSON`          | Message could not be parsed as JSON            |
| `UNKNOWN_MESSAGE_TYPE`  | `type` field is not a recognized message type  |
| `VALIDATION_ERROR`      | Required fields missing or invalid             |
| `MESSAGE_TOO_LONG`      | Message exceeds maximum allowed size           |
| `EMPTY_MESSAGE`         | Message text is empty                          |
| `TRANSLATION_FAILED`    | All translation providers failed               |
| `UNAUTHORIZED`          | JWT missing, invalid, or expired               |
| `ROOM_NOT_FOUND`        | Room does not exist                            |
| `NOT_ROOM_MEMBER`       | User is not a member of this room              |
| `SERVER_ERROR`          | Unexpected server-side error                   |

---

## Constraints & Validation

| Rule                        | Value / Behavior                                    |
|-----------------------------|-----------------------------------------------------|
| Maximum message size        | **4096 bytes** (UTF-8 encoded)                      |
| Minimum message length      | 1 character (after trimming whitespace)             |
| Maximum `username` length   | 50 characters                                       |
| Heartbeat interval          | 30 seconds (client-side)                            |
| Connection timeout          | 90 seconds of no messages                           |
| Reconnect strategy          | Exponential backoff: 1s, 2s, 4s, 8s, max 30s       |
| Max reconnect attempts      | 10 (then notify user of failure)                    |

---

## Behavior for Special Cases

| Case                       | Behavior                                                        |
|----------------------------|-----------------------------------------------------------------|
| Invalid JSON received      | Server sends `ERROR` with code `INVALID_JSON`; keeps connection |
| Unknown message type       | Server sends `ERROR` with code `UNKNOWN_MESSAGE_TYPE`           |
| Empty message text         | Server sends `ERROR` with code `EMPTY_MESSAGE`                  |
| Message too long           | Server sends `ERROR` with code `MESSAGE_TOO_LONG`               |
| Authentication failure     | Server closes connection with WebSocket code `4001`             |
| Unauthorized room          | Server closes connection with WebSocket code `4003`             |
| Translation failure        | Server delivers message with `original_text`, sends `ERROR`     |
| User disconnects           | Server broadcasts `LEAVE` to remaining room members             |
| Server-side error          | Server sends `ERROR` with code `SERVER_ERROR`                   |

---

## WebSocket Close Codes

| Code   | Meaning                |
|--------|------------------------|
| `1000` | Normal closure         |
| `4001` | Unauthorized (JWT)     |
| `4003` | Forbidden (not member) |
| `4004` | Room not found         |

---

## Reconnection Strategy (Client-Side)

```
Disconnect detected
       │
       ▼
Wait 1 second → attempt reconnect
       │
   FAILED ──► Wait 2 seconds → attempt reconnect
       │
   FAILED ──► Wait 4 seconds → attempt reconnect
       │
   FAILED ──► Wait 8 seconds → attempt reconnect
       │
   FAILED ──► ... up to 30 seconds max per attempt
       │
   After 10 failed attempts ──► Notify user: "Connection lost. Please refresh."
```
