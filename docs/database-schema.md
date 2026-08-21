# LinguaChat — Database Schema Contract

> **STATUS: SOURCE OF TRUTH**
> Responsible Engineer: Yousef Khairy
> Any schema change requires Team Leader approval (Ahmed Alammari).
> NEVER store plaintext passwords. NEVER store secrets in the database.

---

## Overview

The database uses **PostgreSQL** accessed via **SQLAlchemy (Async)**.
All tables use UUID primary keys. Timestamps are stored as UTC.

---

## Tables

---

### 1. `users`

Stores registered user accounts.

| Column               | Type         | Constraints                      | Notes                          |
|----------------------|--------------|----------------------------------|--------------------------------|
| `id`                 | UUID         | PRIMARY KEY, default gen_uuid4() | Unique user identifier         |
| `username`           | VARCHAR(50)  | NOT NULL, UNIQUE                 | Alphanumeric + underscore only |
| `hashed_password`    | VARCHAR(255) | NOT NULL                         | Bcrypt hash — NEVER plaintext  |
| `preferred_language` | VARCHAR(10)  | NOT NULL, default 'en'           | ISO 639-1 code (e.g., "ar", "en") |
| `created_at`         | TIMESTAMP    | NOT NULL, default NOW()          | UTC timestamp                  |
| `updated_at`         | TIMESTAMP    | NOT NULL, default NOW()          | Updated on modification        |
| `is_active`          | BOOLEAN      | NOT NULL, default TRUE           | Soft-disable accounts          |

**Indexes**:
- `idx_users_username` on `username` (UNIQUE — implicit from constraint)

**Constraints**:
- `username` must be unique across all users.
- `hashed_password` stores ONLY the bcrypt hash.

---

### 2. `rooms`

Stores chat rooms.

| Column        | Type         | Constraints                          | Notes                          |
|---------------|--------------|--------------------------------------|--------------------------------|
| `id`          | UUID         | PRIMARY KEY, default gen_uuid4()     | Unique room identifier         |
| `name`        | VARCHAR(100) | NOT NULL                             | Display name for the room      |
| `created_by`  | UUID         | NOT NULL, FK → users(id) ON DELETE SET NULL | Creator of the room  |
| `created_at`  | TIMESTAMP    | NOT NULL, default NOW()              | UTC timestamp                  |

**Indexes**:
- `idx_rooms_created_by` on `created_by`

**Relationships**:
- `created_by` → `users.id` (many-to-one)
- Room has many `room_members`
- Room has many `messages`

---

### 3. `room_members`

Join table tracking which users belong to which rooms.

| Column      | Type      | Constraints                          | Notes                       |
|-------------|-----------|--------------------------------------|-----------------------------|
| `id`        | UUID      | PRIMARY KEY, default gen_uuid4()     | Unique membership record    |
| `room_id`   | UUID      | NOT NULL, FK → rooms(id) ON DELETE CASCADE | Target room          |
| `user_id`   | UUID      | NOT NULL, FK → users(id) ON DELETE CASCADE | Member user          |
| `joined_at` | TIMESTAMP | NOT NULL, default NOW()              | UTC timestamp               |

**Indexes**:
- `idx_room_members_room_id` on `room_id`
- `idx_room_members_user_id` on `user_id`
- `uq_room_members_room_user` UNIQUE on `(room_id, user_id)` — prevents duplicates

**Constraints**:
- A user can only appear once per room (UNIQUE constraint on room_id + user_id).

**Relationships**:
- `room_id` → `rooms.id`
- `user_id` → `users.id`

---

### 4. `messages`

Stores all chat messages sent in rooms.

| Column              | Type         | Constraints                              | Notes                           |
|---------------------|--------------|------------------------------------------|---------------------------------|
| `id`                | UUID         | PRIMARY KEY, default gen_uuid4()         | Unique message identifier       |
| `room_id`           | UUID         | NOT NULL, FK → rooms(id) ON DELETE CASCADE | Room this message belongs to |
| `sender_id`         | UUID         | NOT NULL, FK → users(id) ON DELETE SET NULL | Message author              |
| `original_text`     | TEXT         | NOT NULL                                 | Original message content        |
| `original_language` | VARCHAR(10)  | NOT NULL                                 | Detected/declared language code |
| `sent_at`           | TIMESTAMP    | NOT NULL, default NOW()                  | UTC timestamp                   |

**Indexes**:
- `idx_messages_room_id` on `room_id`
- `idx_messages_sender_id` on `sender_id`
- `idx_messages_sent_at` on `sent_at` (for time-based pagination)

**Constraints**:
- `original_text` MUST NOT be empty.
- `original_language` MUST be a valid ISO 639-1 code.

**Relationships**:
- `room_id` → `rooms.id` (many-to-one)
- `sender_id` → `users.id` (many-to-one)
- Message has many `translations`

---

### 5. `translations`

Caches translated versions of messages per target language.

| Column             | Type        | Constraints                              | Notes                            |
|--------------------|-------------|------------------------------------------|----------------------------------|
| `id`               | UUID        | PRIMARY KEY, default gen_uuid4()         | Unique translation record        |
| `message_id`       | UUID        | NOT NULL, FK → messages(id) ON DELETE CASCADE | Source message            |
| `target_language`  | VARCHAR(10) | NOT NULL                                 | ISO 639-1 target language code   |
| `translated_text`  | TEXT        | NOT NULL                                 | Translated content               |
| `provider_used`    | VARCHAR(50) | NOT NULL                                 | "libretranslate", "google", "cache" |
| `confidence`       | FLOAT       | NULLABLE                                 | 0.0–1.0 or null                  |
| `created_at`       | TIMESTAMP   | NOT NULL, default NOW()                  | UTC timestamp                    |

**Indexes**:
- `idx_translations_message_id` on `message_id`
- `uq_translations_message_lang` UNIQUE on `(message_id, target_language)` — one translation per lang per message

**Constraints**:
- Only ONE translation per `(message_id, target_language)` pair (UNIQUE constraint).
- `confidence` may be null if the provider does not return confidence scores.

**Relationships**:
- `message_id` → `messages.id` (many-to-one)

---

## Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│    users     │────────►│   room_members   │◄────────│    rooms     │
│              │  1:N    │                  │  N:1    │              │
│ id (PK)      │         │ id (PK)          │         │ id (PK)      │
│ username     │         │ room_id (FK)     │         │ name         │
│ hashed_pwd   │         │ user_id (FK)     │         │ created_by   │
│ pref_lang    │         │ joined_at        │         │   (FK→users) │
│ created_at   │         └──────────────────┘         │ created_at   │
│ updated_at   │                                      └──────┬───────┘
│ is_active    │                                             │
└──────┬───────┘                                             │ 1:N
       │ 1:N                                                 ▼
       │                                           ┌──────────────────┐
       └──────────────────────────────────────────►│    messages      │
                                                   │                  │
                                                   │ id (PK)          │
                                                   │ room_id (FK)     │
                                                   │ sender_id (FK)   │
                                                   │ original_text    │
                                                   │ original_lang    │
                                                   │ sent_at          │
                                                   └──────┬───────────┘
                                                          │ 1:N
                                                          ▼
                                                ┌──────────────────────┐
                                                │     translations     │
                                                │                      │
                                                │ id (PK)              │
                                                │ message_id (FK)      │
                                                │ target_language      │
                                                │ translated_text      │
                                                │ provider_used        │
                                                │ confidence           │
                                                │ created_at           │
                                                └──────────────────────┘
```

---

## Migration Policy

- All schema changes MUST be applied via **Alembic** migrations.
- Migration files MUST be committed alongside model changes.
- Never alter the `users.hashed_password` column type or remove it.
- Never store secrets, API keys, or tokens in any table.

---

## Security Rules

- `hashed_password` is write-only from application perspective — never returned in API responses.
- `id` fields (UUIDs) are safe to expose in responses.
- No column may store raw passwords, API keys, or JWT secrets.
