# LinguaChat — Architecture Document

> **STATUS: SOURCE OF TRUTH**
> All team members and AI agents MUST read this document before writing any code.
> Any architectural change requires explicit approval from the Team Leader (Ahmed Alammari).

---

## 1. System Overview

LinguaChat is a real-time, multilingual chat system built on a Client/Server architecture.
Users authenticate, create or join rooms, and exchange messages that are automatically
translated into each recipient's preferred language.

---

## 2. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                      CLIENT                         │
│               React Frontend (SPA)                  │
│  pages/ components/ hooks/ services/ api/ types/    │
└──────────────────────┬──────────────────────────────┘
                       │
           ┌───────────┴────────────┐
           │ REST (HTTP/JSON)       │ WebSocket (ws://)
           │ POST /auth/login       │ /ws/{room_id}
           │ POST /rooms            │
           │ GET  /rooms            │
           │ etc.                   │
           └───────────┬────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                 FASTAPI BACKEND                      │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  auth/   │  │  rooms/  │  │   websocket/     │  │
│  │ router   │  │ router   │  │   router         │  │
│  │ service  │  │ service  │  │   manager        │  │
│  │ schemas  │  │ schemas  │  │   protocol       │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │             │                 │             │
│  ┌────▼─────────────▼─────────────────▼──────────┐ │
│  │              BUSINESS LOGIC LAYER              │ │
│  │   users/   messages/   translation/   dashboard│ │
│  └────┬──────────────┬──────────┬────────────────┘ │
│       │              │          │                   │
│  ┌────▼──────┐  ┌────▼──┐  ┌───▼───────────────┐   │
│  │ database/ │  │       │  │   translation/    │   │
│  │ session   │  │ msgs  │  │   service         │   │
│  │ models/   │  │       │  │   providers       │   │
│  └────┬──────┘  └───────┘  │   detector        │   │
│       │                    │   cache           │   │
│       │                    └───────────────────┘   │
└───────┼────────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────────────────┐
│              INFRASTRUCTURE                         │
│   PostgreSQL    Redis (Cache)    LibreTranslate     │
└────────────────────────────────────────────────────┘
```

---

## 3. Layer Responsibilities

### 3.1 Frontend (React)
- **Responsibility**: Rendering UI, user interaction, state management.
- **Communicates with**: FastAPI via REST and WebSocket.
- **MUST NOT**: Contain any Database logic, Translation Provider logic, or business rules.
- **Location**: `frontend/src/`

### 3.2 REST API Layer (FastAPI Routers)
- **Responsibility**: Receive HTTP requests, validate input, delegate to services, return responses.
- **Modules**: `auth/router.py`, `rooms/router.py`, `users/router.py`, `dashboard/router.py`
- **MUST NOT**: Contain business logic directly — delegate to service layer.

### 3.3 WebSocket Layer
- **Responsibility**: Maintain persistent connections, route real-time messages, handle protocol.
- **Modules**: `websocket/router.py`, `websocket/manager.py`, `websocket/protocol.py`
- **MUST NOT**: Implement Translation logic directly. Call Translation Service via interface.
- **MUST NOT**: Implement Database queries directly. Use Message Service.

### 3.4 Business Logic Layer (Services)
- **Responsibility**: All application logic — room management, message handling, user operations.
- **Modules**: `users/service.py`, `rooms/service.py`, `messages/service.py`, `dashboard/service.py`
- **MUST NOT**: Contain HTTP-specific logic (status codes, headers).

### 3.5 Translation Module
- **Responsibility**: Language detection, translation, caching, provider abstraction.
- **Modules**: `translation/service.py`, `translation/providers.py`, `translation/detector.py`, `translation/cache.py`
- **MUST NOT**: Know about WebSocket internals or Database schema details.
- **Interface**: See `docs/translation-contract.md`.

### 3.6 Authentication Module
- **Responsibility**: User registration, login, JWT issuance and validation.
- **Modules**: `auth/router.py`, `auth/service.py`, `auth/schemas.py`
- **MUST NOT**: Handle room logic, message logic, or translation.

### 3.7 Database Layer
- **Responsibility**: Database session management, ORM models, migrations.
- **Modules**: `database/session.py`, `database/base.py`, `database/models/`
- **MUST NOT**: Contain business logic. Purely data access.
- **MUST NOT**: Know about React, HTTP, or WebSocket internals.

### 3.8 Core Module
- **Responsibility**: Application configuration, security utilities, shared error definitions.
- **Modules**: `core/config.py`, `core/security.py`, `core/errors.py`

---

## 4. Module Boundary Rules

| Module         | Can Call                              | CANNOT Call                         |
|----------------|---------------------------------------|-------------------------------------|
| Frontend       | REST API, WebSocket                   | Database, Translation Providers     |
| WebSocket      | Translation Service, Message Service  | Database directly, Frontend         |
| Translation    | Cache, Providers, Detector            | WebSocket, Database models directly |
| Auth           | Database, Core/Security               | Rooms, Messages, Translation        |
| Rooms          | Database, Auth (validate)             | Translation, WebSocket internals    |
| Messages       | Database, Translation Service         | Auth internals, WebSocket internals |
| Dashboard      | Database (read-only aggregations)     | Translation, WebSocket              |
| Database Layer | None (it is the bottom layer)         | Everything above it                 |

---

## 5. Data Flow: Message Translation

```
User A sends "السلام عليكم" (Arabic)
       │
       ▼
WebSocket /ws/{room_id}
       │
       ▼
websocket/manager.py  ──► Broadcasts raw message to room
       │
       ▼
translation/service.py.translate_message(text, source, target)
       │
       ├──► translation/cache.py         [Cache Lookup]
       │         │
       │    Cache HIT ──► return cached translation
       │    Cache MISS ──►
       │         │
       ├──► translation/providers.py     [Primary: LibreTranslate]
       │         │
       │    SUCCESS ──► cache result ──► return
       │    FAILURE ──►
       │         │
       └──► translation/providers.py     [Fallback Provider]
                 │
                 └──► Unified Response: {translated_text, source_used, confidence}
       │
       ▼
User B receives: "Hello" (English) + original Arabic preserved
```

---

## 6. Technology Stack

| Component          | Technology                      |
|--------------------|---------------------------------|
| Frontend           | React (Vite)                    |
| Backend Framework  | FastAPI                         |
| Database           | PostgreSQL                      |
| ORM                | SQLAlchemy (Async)              |
| Authentication     | JWT (python-jose)               |
| Real-time          | WebSocket (built into FastAPI)  |
| Translation        | LibreTranslate (Primary)        |
| Translation Cache  | Redis (or in-memory fallback)   |
| Language Detection | langdetect (or equivalent)      |
| Testing (Backend)  | Pytest + pytest-asyncio         |
| Testing (Frontend) | Vitest / React Testing Library  |
| Containerization   | Docker + docker-compose         |

---

## 7. Edge Cases — Module Ownership

| Edge Case                        | Responsible Module           |
|----------------------------------|------------------------------|
| Empty message                    | websocket/protocol.py        |
| Extremely long message           | websocket/protocol.py        |
| Invalid username                 | auth/schemas.py              |
| Duplicate username               | auth/service.py              |
| Invalid language code            | translation/detector.py      |
| Unsupported language             | translation/service.py       |
| Invalid JWT                      | core/security.py             |
| Expired JWT                      | core/security.py             |
| Missing JWT                      | auth/router.py (dependency)  |
| Unauthorized room access         | rooms/service.py             |
| Invalid room ID                  | rooms/service.py             |
| User already in room             | rooms/service.py             |
| User disconnects                 | websocket/manager.py         |
| Network failure / reconnect      | websocket/manager.py + Frontend |
| Invalid WebSocket message        | websocket/protocol.py        |
| Unknown WebSocket message type   | websocket/protocol.py        |
| Translation provider failure     | translation/service.py       |
| Translation timeout              | translation/service.py       |
| Fallback translation failure     | translation/service.py       |
| Cache miss                       | translation/cache.py         |
| Cache failure                    | translation/cache.py         |
| Database failure                 | database/session.py          |
| Duplicate requests               | rooms/service.py             |
| Malformed JSON                   | websocket/protocol.py        |
| Server 500 error                 | core/errors.py               |

---

## 8. Change Policy

> **Any architectural change MUST be approved by Team Leader: Ahmed Alammari**
> before implementation.

Steps to propose a change:
1. Stop implementation.
2. Open a discussion with Team Leader.
3. Update this document ONLY after explicit approval.
4. Notify all team members of the change.
