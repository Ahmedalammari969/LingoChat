# LinguaChat

> Real-time multilingual chat — one message, every language.

---

## Project Overview

**LinguaChat** is a Client/Server real-time chat system where users communicate across language barriers.
Messages are automatically detected, translated, and delivered in each recipient's preferred language — instantly.

**Stack**: React · FastAPI · PostgreSQL · SQLAlchemy Async · WebSocket · LibreTranslate · Redis · JWT · Docker

---

## Architecture at a Glance

```
Client (React) ──► REST API + WebSocket ──► FastAPI ──► PostgreSQL
                                                  └──► Translation Service (LibreTranslate + Fallback)
                                                  └──► Redis Cache
```

Full details: [`docs/architecture.md`](docs/architecture.md)

---

## Team & Responsibilities

| Member              | Role                                  | Module Ownership                                                                    |
|---------------------|---------------------------------------|-------------------------------------------------------------------------------------|
| **Ahmed Alammari**  | Team Leader / Architect / Frontend    | Architecture · Contracts · `frontend/` · Integration · Testing · Final Review      |
| **Mohammed Al-Daees** | WebSocket & Realtime Engineer       | `backend/app/websocket/` · Connection Manager · Heartbeat · WebSocket Tests        |
| **Moayad Al-Soufi** | Translation & Business Logic Engineer | `backend/app/translation/` · Language Detection · LibreTranslate · Fallback · Cache |
| **Yousef Khairy**   | Database / Auth / REST API Engineer   | `backend/app/database/` · `backend/app/auth/` · `backend/app/rooms/` · `backend/app/messages/` · `backend/app/dashboard/` · REST API · JWT |

---

## Project Structure

```
linguachat/
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── core/                     # Config, Security utilities, Error definitions
│   │   ├── auth/                     # Authentication endpoints & JWT logic
│   │   ├── users/                    # User management
│   │   ├── rooms/                    # Room creation, joining, listing
│   │   ├── websocket/                # WebSocket gateway & real-time messaging
│   │   ├── translation/              # Language detection, translation, cache
│   │   ├── messages/                 # Message persistence & retrieval
│   │   ├── dashboard/                # Aggregate stats API
│   │   └── database/                 # SQLAlchemy models & session
│   ├── tests/
│   │   ├── unit/                     # Unit tests
│   │   ├── integration/              # Integration tests
│   │   └── websocket/                # WebSocket-specific tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/                      # API client functions
│   │   ├── components/               # Reusable UI components
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── pages/                    # Page components (Login, Rooms, Chat, Dashboard)
│   │   ├── services/                 # WebSocket service, auth service
│   │   ├── types/                    # TypeScript/JSDoc type definitions
│   │   ├── utils/                    # Utility functions
│   │   └── App.jsx                   # Root application component
│   ├── package.json
│   └── .env.example
├── docs/
│   ├── architecture.md               # SOURCE OF TRUTH — System architecture
│   ├── api-contract.md               # SOURCE OF TRUTH — REST API endpoints
│   ├── websocket-contract.md         # SOURCE OF TRUTH — WebSocket protocol
│   ├── database-schema.md            # SOURCE OF TRUTH — Database schema
│   ├── translation-contract.md       # SOURCE OF TRUTH — Translation service interface
│   └── security.md                   # SOURCE OF TRUTH — Security guidelines
├── _integration/
│   ├── DELIVERY_TEMPLATE.md          # Task delivery report template
│   ├── Mohammed/                     # Mohammed's task deliveries
│   ├── Moayad/                       # Moayad's task deliveries
│   └── Yousef/                       # Yousef's task deliveries
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values

uvicorn app.main:app --reload
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env if needed

npm run dev
```

Frontend runs at: `http://localhost:3000`

### Docker (Full Stack)

```bash
docker-compose up --build
```

---

## Documentation Contracts

> All documents below are **SOURCE OF TRUTH**.
> Read them BEFORE writing any code. Change them ONLY with Team Leader approval.

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | System architecture, layers, module boundaries, data flow |
| [`docs/api-contract.md`](docs/api-contract.md) | REST API endpoints, request/response schemas, error codes |
| [`docs/websocket-contract.md`](docs/websocket-contract.md) | WebSocket protocol, message types, reconnection strategy |
| [`docs/database-schema.md`](docs/database-schema.md) | Database tables, columns, constraints, relationships |
| [`docs/translation-contract.md`](docs/translation-contract.md) | Translation service interface, provider flow, cache |
| [`docs/security.md`](docs/security.md) | Security rules, JWT, password hashing, logging policy |

---

## Team Collaboration Rules

1. **One project** — no member has a separate repository or separate backend.
2. **Module ownership** — each member is responsible for their designated modules only.
3. **Before modifying a Contract** (API, WebSocket, Database, Translation, Architecture):
   - **STOP** implementation immediately.
   - Notify Team Leader (Ahmed Alammari).
   - Wait for explicit written approval.
   - Update the contract document.
   - Notify all team members.
4. **Task Delivery** — when a task is complete, fill out `_integration/DELIVERY_TEMPLATE.md`
   and place it in your `_integration/<YourName>/` folder.
5. **No cross-module changes** — do not modify another member's module without their agreement and Team Leader approval.
6. **Test before delivery** — do not submit untest code.
7. **Report blockers early** — if you are blocked, report to Team Leader immediately.

---

## Task Delivery Process

When a task is complete, each developer MUST submit a delivery report:

1. Copy `_integration/DELIVERY_TEMPLATE.md`
2. Fill in all sections (Task ID, Files Created, Tests, Security Checks, etc.)
3. Save as `_integration/<YourName>/TASK-XX-<YOUR_NAME>.md`
4. Notify Ahmed Alammari for review.

**Required fields in delivery report**:

| Field | Description |
|-------|-------------|
| Task ID | Unique task identifier |
| Developer | Your name |
| Files Created | Full paths of new files |
| Files Modified | Full paths of modified files |
| Implementation | Summary of what was built |
| Tests | Test files and what they test |
| Test Results | Actual test output |
| Edge Cases | Which edge cases from architecture.md were handled |
| Security Checks | Confirm you followed security.md |
| Dependencies | New packages added |
| Contracts Used | Which contract documents were followed |
| Known Problems | Any unresolved issues |
| Integration Notes | What other members need to know |
| Required Leader Action | Decisions needed from Ahmed |

---

## AI DEVELOPMENT RULES

> These rules apply to any AI agent (including Antigravity/Gemini) working on this project.

1. **AI must read documentation before coding.**
   Read all relevant contract documents in `docs/` before writing a single line of code.

2. **AI must not invent APIs.**
   Only implement endpoints defined in `docs/api-contract.md`.

3. **AI must not invent WebSocket message formats.**
   Only use message types defined in `docs/websocket-contract.md`.

4. **AI must not change database schema without approval.**
   The schema is defined in `docs/database-schema.md`. Any deviation requires Team Leader approval.

5. **AI must not change architecture without approval.**
   The architecture is defined in `docs/architecture.md`.

6. **AI must not create duplicate services.**
   One authentication system, one translation service, one WebSocket manager.

7. **AI must not create duplicate authentication systems.**
   Authentication is in `backend/app/auth/` only.

8. **AI must not hardcode secrets.**
   All secrets come from environment variables.

9. **AI must not expose sensitive information.**
   No passwords, API keys, JWT secrets, or tokens in code, logs, or responses.

10. **AI must work only on the assigned task.**
    Do not build features not explicitly requested.

11. **AI must preserve existing code.**
    Do not delete or rewrite code from other modules without explicit instruction.

12. **AI must run tests.**
    Always run tests after making changes. Report results.

13. **AI must report modified files.**
    At the end of every task, list every file created or modified.

14. **AI must report dependencies.**
    List any new packages added to `requirements.txt` or `package.json`.

15. **AI must report unresolved issues.**
    Do not silently leave broken or incomplete code. Report it.

16. **AI must stop if a contract conflict is detected.**
    If the assigned task conflicts with a contract, stop and report:
    `ARCHITECTURAL DECISION REQUIRED` with the conflict details.

17. **AI must never silently change a contract.**
    Contract documents are changed ONLY after explicit approval. Never edit them unilaterally.

18. **AI must not build features that were not requested.**
    The current Task ID defines the scope. Nothing more.

---

## Running Tests

### Backend

```bash
cd backend
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/websocket/ -v
```

### Frontend

```bash
cd frontend
npm test
```

---

## Environment Variables

See [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example).
Never commit `.env` files with real values.

---

## License

Academic project — LinguaChat — All rights reserved by the project team.
