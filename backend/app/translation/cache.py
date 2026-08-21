from __future__ import annotations
"""
LinguaChat — Translation Cache (Skeleton)

Redis-backed cache for translation results.
Implementation: Moayad Al-Soufi — TASK: Translation Service
See: docs/translation-contract.md § 4. Cache Contract

ARCHITECTURE FREEZE (2026-08-13):
Redis is OPTIONAL. The application must start and work without Redis.
Default backend: in-memory dictionary (process-scoped, non-persistent).
Redis backend: active only when REDIS_URL is set in environment.

Cache failures MUST be non-fatal — always fall through to provider calls.
"""

import hashlib
from typing import Optional


def _cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """
    Build a deterministic cache key.
    Format: translate:{source_lang}:{target_lang}:{sha256(text)}
    See: docs/translation-contract.md § Cache Key Format
    """
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"translate:{source_lang}:{target_lang}:{text_hash}"


async def get_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[dict]:
    """
    Retrieve a cached translation result.

    Returns:
        Translation dict with source_used="cache", or None on cache miss.

    Backend selection (implementation by Moayad Al-Soufi):
    - If REDIS_URL is configured → use Redis
    - Otherwise → use in-memory fallback (_memory_cache below)
    - Any backend failure MUST return None (non-fatal)

    See: docs/translation-contract.md § 4
    """
    raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")


async def set_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str,
    translation: dict,
    ttl_seconds: int = 3600,
) -> None:
    """
    Store a translation result in cache with TTL.

    Backend selection (implementation by Moayad Al-Soufi):
    - If REDIS_URL is configured → use Redis (with TTL via EXPIRE)
    - Otherwise → use in-memory fallback (_memory_cache below)
      Note: in-memory cache does NOT enforce TTL natively — implement a
      timestamp-based expiry check or use a library like cachetools.
    - MUST NOT raise if cache backend is unavailable — log and return silently.

    See: docs/translation-contract.md § 4
    """
    raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")


# ── In-Memory Fallback Cache ───────────────────────────────────────────────────
# Used when Redis is not configured.
# Structure: {cache_key: {"value": dict, "expires_at": float}}
# Moayad Al-Soufi: populate and read from this dict when REDIS_URL is absent.
# This is process-scoped and NOT shared across workers or restarts.
_memory_cache: dict = {}
