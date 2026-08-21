# LinguaChat — Translation Service Contract

> **STATUS: SOURCE OF TRUTH — FROZEN (Architecture Decision, 2026-08-13)**
> Responsible Engineer: Moayad Al-Soufi
> All consumers of the Translation Service MUST use only this interface.
> The internal implementation details (which provider is used) are hidden from consumers.
> Any change to this interface requires Team Leader approval (Ahmed Alammari).

---

## 1. Overview

The Translation Service is a **pure abstraction layer**. Consumers (WebSocket Manager, Message Service)
do NOT know which provider is being used. They call `translate_message()` and receive a unified response.

---

## 2. Primary Function Contract

### `translate_message`

```python
async def translate_message(
    text: str,
    source_lang: str,
    target_lang: str
) -> dict:
    """
    Translate text from source_lang to target_lang.

    Args:
        text:        The text content to translate. Must not be empty.
        source_lang: ISO 639-1 language code of the source text (e.g., "ar").
                     Pass "auto" to trigger automatic language detection.
        target_lang: ISO 639-1 language code of the desired output (e.g., "en").

    Returns:
        A dictionary with the following structure:
        {
            "translated_text": str,       # The translated content
            "source_used": str,           # Provider that fulfilled the request
            "confidence": float | None    # 0.0–1.0 or None if not available
        }

    Raises:
        TranslationError: If ALL providers fail and no cache entry exists.
    """
```

### Return Value Schema

```json
{
  "translated_text": "Hello",
  "source_used": "libretranslate",
  "confidence": 0.95
}
```

| Field            | Type           | Required | Description                                                                                 |
|------------------|----------------|----------|---------------------------------------------------------------------------------------------|
| `translated_text`| string         | Yes      | The translated output                                                                       |
| `source_used`    | string         | Yes      | One of: `"libretranslate"`, `"google"`, `"cache"`, `"identity"`                            |
| `confidence`     | float or null  | Yes      | 0.0–1.0 confidence score, or `null` if not available                                        |

> **`"identity"`**: returned when `source_lang == target_lang`. No provider is called. The original text
> is returned unchanged with `confidence = 1.0`. The Gateway MUST NOT know how this is handled internally.

---

## 3. Language Detection Contract

### `detect_language`

```python
async def detect_language(text: str) -> str:
    """
    Detect the language of the provided text.

    Args:
        text: The text to analyze. Must be non-empty.

    Returns:
        ISO 639-1 language code (e.g., "ar", "en", "fr").
        Returns "unknown" if detection fails.

    Notes:
        - Never raises an exception; returns "unknown" on failure.
        - A returned "unknown" code MUST be handled by the caller.
    """
```

---

## 4. Cache Contract

The cache module provides a transparent caching layer for translations.

### Cache Backend — Redis (Optional)

> **DECISION (2026-08-13):** Redis is OPTIONAL. The application MUST start and work correctly without Redis.
> The default cache backend is an **in-memory dictionary** (process-scoped, non-persistent).
> Redis may be configured as an upgraded backend via the `REDIS_URL` environment variable.
> Cache failures (Redis unavailable) MUST be non-fatal — fall through to provider calls silently.

### Cache Key Format

```
translate:{source_lang}:{target_lang}:{sha256(text)}
```

- Key components are separated by `:`
- Text is hashed (SHA-256) to keep keys predictable and avoid injection.

### Cache Interface

```python
async def get_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str
) -> dict | None:
    """Returns cached translation dict or None on cache miss.
    Uses Redis if configured, otherwise in-memory fallback."""

async def set_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str,
    translation: dict,
    ttl_seconds: int = 3600
) -> None:
    """Stores a translation in cache with TTL.
    Must not raise if cache backend is unavailable."""
```

### Cache `source_used` Value

When returning a cached result, the `source_used` field MUST be set to `"cache"`.

---

## 5. Translation Flow

```
Caller: translate_message(text, source_lang, target_lang)
        │
        ▼
[1] source_lang == "auto"?
        │
   YES ─┤
        ▼
   detect_language(text)
        │   Returns ISO code or "unknown"
        │
        ▼ (resolved source_lang)
        │
   NO  ─┘
        │
        ▼
[2] source_lang == target_lang?
        │
   YES ──► Return immediately (no provider call):
           {
             "translated_text": text,  (same, no translation needed)
             "source_used": "identity",
             "confidence": 1.0
           }
           (Gateway does NOT know this shortcut exists)
        │
   NO  ──►
        │
        ▼
[3] Cache Lookup
        │
   HIT ──► Return cached result with source_used="cache"
        │
   MISS ──►
        │
        ▼
[4] Primary Provider: LibreTranslate
        │
   SUCCESS ──► cache result ──► return result
        │
   FAILURE (timeout / error) ──►
        │
        ▼
[5] Fallback Provider (e.g., Google Translate or other)
        │
   SUCCESS ──► cache result ──► return result
        │
   FAILURE ──►
        │
        ▼
[6] Raise TranslationError
    (caller must handle and deliver original_text to user)
```

---

## 6. Provider Interface

All providers MUST implement this interface (Python Protocol/ABC):

```python
class TranslationProvider:
    """Abstract interface for translation providers."""

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> dict:
        """
        Returns:
            {
                "translated_text": str,
                "source_used": str,   # provider name
                "confidence": float | None
            }
        Raises:
            ProviderError on failure.
        """
        ...
```

**Registered Providers** (in priority order):
1. Cache lookup — `source_used = "cache"` on hit
2. `LibreTranslateProvider` — primary (`source_used = "libretranslate"`)
3. `GoogleTranslateProvider` — fallback (`source_used = "google"`)
   - **OPTIONAL**: only active when `GOOGLE_TRANSLATE_API_KEY` env var is set.
   - If key is not set, this provider MUST be skipped silently (not raise an error).
   - If key IS set, Google is tried after LibreTranslate failure.
4. `TranslationError` — raised if all active providers fail

---

## 7. Error Handling

```python
class TranslationError(Exception):
    """Raised when all translation providers fail."""
    pass

class ProviderError(Exception):
    """Raised by a specific provider on failure."""
    pass
```

**Rule**: The `translate_message` function MUST NOT expose provider-specific errors to consumers.
Wrap all provider exceptions in `TranslationError`.

---

## 8. Supported Languages

The initial list of supported languages is determined by LibreTranslate's available languages.
The system MUST handle requests for unsupported languages gracefully (return `TranslationError`).

Common supported codes: `ar`, `en`, `fr`, `de`, `es`, `zh`, `ru`, `ja`, `pt`, `it`

---

## 9. Constraints

| Constraint              | Value                                                               |
|-------------------------|---------------------------------------------------------------------|
| Max text length         | 5000 characters                                                     |
| Min text length         | 1 character                                                         |
| Provider timeout        | 10 seconds per provider                                             |
| Cache TTL               | 3600 seconds (1 hour) by default                                    |
| Cache backend           | In-memory (default, non-persistent) or Redis (optional via env var) |
| `source_used` values    | `"libretranslate"`, `"google"`, `"cache"`, `"identity"`            |
| confidence range        | 0.0 – 1.0 or `null`                                                 |
| Google fallback         | Optional — active only when `GOOGLE_TRANSLATE_API_KEY` is set       |

---

## 10. What Consumers MUST Do

- Always check if `translated_text` is non-empty before delivering.
- Handle `TranslationError` by delivering `original_text` to the user.
- Never access `providers.py` directly — always go through `service.py`.
- Never bypass the cache.
