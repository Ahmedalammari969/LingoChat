# LinguaChat — Security Guidelines

> **STATUS: SOURCE OF TRUTH**
> All team members and AI agents MUST follow these guidelines.
> Security violations must be reported to Team Leader (Ahmed Alammari) immediately.

---

## 1. Secrets Management

### Golden Rule
> **NEVER commit secrets, passwords, API keys, or tokens to source control.**

### Rules

- All secrets are managed via **environment variables** only.
- Use `.env` files **locally** — they are listed in `.gitignore`.
- Use `.env.example` for documentation — contains **placeholder values only** (no real secrets).
- In production, use a secrets manager (Docker secrets, environment injection via CI/CD).
- JWT secrets MUST be cryptographically random strings of at least 32 characters.

### Forbidden

```python
# FORBIDDEN — never do this
JWT_SECRET = "mysecret123"
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-abc123..."
```

### Correct

```python
# CORRECT — always do this
import os
JWT_SECRET = os.getenv("JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## 2. Password Hashing

- Passwords MUST be hashed using **bcrypt** before storage.
- Use `passlib[bcrypt]` library.
- The cost factor MUST be at least **12**.
- NEVER log passwords — not even hashed ones.
- NEVER return `hashed_password` in any API response.
- NEVER compare passwords using plain string equality.

```python
# CORRECT usage pattern (implementation by Yousef Khairy)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## 3. JWT (JSON Web Tokens)

### Token Format
- Algorithm: **HS256**
- Payload fields: `sub` (user_id), `exp` (expiry), `iat` (issued at)
- Default expiry: **1 hour** (configurable via env var)
- Library: `python-jose[cryptography]`

### Rules
- The JWT secret MUST come from `JWT_SECRET` environment variable.
- Tokens MUST be validated on every protected endpoint.
- Tokens MUST be validated on WebSocket connection (via query param `?token=...`).
- Expired tokens MUST return `401 Unauthorized` — not `403`.
- Invalid tokens MUST return `401 Unauthorized`.
- Missing tokens on protected routes MUST return `401 Unauthorized`.
- Tokens MUST NOT be logged.

### Token Validation Dependency (FastAPI)

```python
# Pattern — actual implementation by Yousef Khairy
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # validate JWT, raise 401 on failure
    ...
```

### Frontend Token Storage — localStorage (Approved Decision)

> **DECISION (Architecture Freeze 2026-08-13):** JWT will be stored in browser `localStorage`.
> This is an explicitly approved decision for this academic project.

#### Security Tradeoff

| Factor | localStorage (current choice) | httpOnly Cookie (alternative) |
|--------|-------------------------------|-------------------------------|
| XSS risk | **Higher** — JS can read the token | Lower — JS cannot access |
| CSRF risk | Lower — no automatic sending | Higher — requires CSRF token |
| Implementation complexity | Simple | Requires cookie config + CSRF |
| Suitable for | Academic / development | Production applications |

This tradeoff is **accepted for this project**. httpOnly cookies are recommended for production deployments.

#### Rules for localStorage JWT (MANDATORY)

- **NEVER** store the user's password in `localStorage` or anywhere in the browser.
- **NEVER** log the JWT value in `console.log()` or any logging output.
- **NEVER** hardcode a JWT secret or token in source code.
- JWT **MUST** have an expiration (`exp` claim) — non-expiring tokens are forbidden.
- All API requests **MUST** send the JWT via `Authorization: Bearer <token>` header.
- WebSocket connections **MUST** pass the JWT as `?token=<jwt>` query parameter per `docs/websocket-contract.md`.
- On logout, the token **MUST** be removed from `localStorage` immediately.
- Do **NOT** implement refresh-token architecture in this project phase.

```js
// CORRECT — set after login
localStorage.setItem('linguachat_token', result.access_token)

// CORRECT — read for API requests
const token = localStorage.getItem('linguachat_token')

// CORRECT — clear on logout
localStorage.removeItem('linguachat_token')

// FORBIDDEN
console.log('token:', token)           // never log
localStorage.setItem('password', ...)  // never store passwords
```

---

## 4. WebSocket Authentication

- Clients pass JWT as query parameter: `/ws/{room_id}?token=<jwt>`
- Server validates JWT **before** establishing WebSocket connection.
- On invalid/missing JWT: close with WebSocket code `4001`.
- On valid JWT but unauthorized room: close with WebSocket code `4003`.
- Tokens in query params MUST be validated immediately — not stored.
- WebSocket connections MUST be closed if the JWT expires during the session.
  - Implementation: periodic re-validation (every heartbeat) — decision by Mohammed Al-Daees.

---

## 5. Authorization & Room Membership

- Room membership MUST be verified on:
  - `GET /rooms/{room_id}/messages` — HTTP
  - `POST /rooms/{room_id}/join` — HTTP
  - WebSocket connection to `/ws/{room_id}`
  - Any WebSocket message delivery targeting a room

- Users MUST NOT receive messages from rooms they are not members of.
- Room membership validation is the responsibility of `rooms/service.py`.

---

## 6. Input Validation

- All request bodies are validated via **Pydantic** schemas.
- All WebSocket messages are validated via `websocket/protocol.py`.
- Validation failures return `422 Unprocessable Entity` (HTTP) or `ERROR` message (WebSocket).
- Validation MUST happen **before** any database operation.

### Specific Rules
- `username`: alphanumeric + underscore, 3–50 chars, no SQL-injectable characters.
- `password`: minimum 8 characters, no maximum length (bcrypt handles it).
- `preferred_language`: must be a valid ISO 639-1 code.
- `room_id`: must be a valid UUID.
- Message text: max 4096 bytes (WebSocket), non-empty.

---

## 7. CORS Strategy

- CORS is configured in `main.py` via FastAPI `CORSMiddleware`.
- In **development**: allow `http://localhost:3000` (React dev server).
- In **production**: allow only the specific frontend domain (via `ALLOWED_ORIGINS` env var).
- NEVER use `allow_origins=["*"]` in production.
- Allowed methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`.
- Allowed headers: `Content-Type`, `Authorization`.

---

## 8. Rate Limiting Strategy

> **ARCHITECTURAL DECISION REQUIRED** — Rate limiting implementation is planned for a future task.

Planned approach (to be implemented by Yousef Khairy):
- Use `slowapi` or middleware-based rate limiting.
- Limits:
  - `/auth/register`: 5 requests/minute per IP
  - `/auth/login`: 10 requests/minute per IP
  - General API: 100 requests/minute per user

---

## 9. Database Security

- Use parameterized queries / SQLAlchemy ORM only — no raw SQL string formatting.
- Database credentials MUST come from `DATABASE_URL` environment variable.
- The `hashed_password` column MUST NEVER be returned in query results used by API responses.
- Database connection pool timeout and max connections MUST be configured (not unbounded).
- Use least-privilege database user for the application.

---

## 10. Error Handling & Information Disclosure

- Production error responses MUST NOT include internal stack traces.
- Use generic error messages for security-sensitive failures:
  - For login failures: `"Invalid username or password"` (NOT `"User not found"` or `"Wrong password"`)
  - For JWT failures: `"Unauthorized"` (NOT token internals)
- Detailed errors are logged server-side only.
- Error format follows the standard defined in `docs/api-contract.md`.

---

## 11. Logging Rules

### MUST log
- Authentication failures (without sensitive data).
- Authorization failures.
- Server errors (500-level).
- Translation provider failures.
- WebSocket connection events (connect/disconnect).

### MUST NOT log
- Passwords (plain or hashed).
- JWT tokens.
- API keys.
- Full message content (for privacy — log message ID only).
- Database connection strings.

---

## 12. Sensitive Information in Code

The following MUST NEVER appear in source code:

| Category           | Examples                                      |
|--------------------|-----------------------------------------------|
| Passwords          | User passwords, database passwords            |
| API Keys           | LibreTranslate API key, Google API key        |
| JWT Secrets        | Any string used to sign JWTs                  |
| Database URLs      | With embedded credentials                    |
| Private Keys       | RSA/EC private keys                          |

Use `.env.example` with placeholder values only:
```
DATABASE_URL=
JWT_SECRET=
LIBRETRANSLATE_URL=
FALLBACK_TRANSLATION_API_KEY=
```

---

## 13. Dependency Security

- Dependencies are pinned in `requirements.txt`.
- Run `pip audit` or `safety check` before each release.
- Do not use dependencies with known critical CVEs.
- Minimum Python version: 3.11+

---

## 14. Edge Cases — Security

| Case                          | Expected Behavior                              |
|-------------------------------|------------------------------------------------|
| Empty password field          | Validation error 422 — before any DB call     |
| SQL injection attempt in input| Pydantic validation rejects invalid chars      |
| Forged JWT signature          | 401 Unauthorized                              |
| Tampered JWT payload          | 401 Unauthorized (signature mismatch)         |
| JWT with future `iat`         | Reject — treat as invalid                    |
| Very long input strings       | Pydantic length validators reject them        |
| CORS from unknown origin      | CORS middleware blocks in production          |
| Duplicate room join           | 409 Conflict — not a security error           |
| Accessing another user's data | 403 Forbidden                                 |
