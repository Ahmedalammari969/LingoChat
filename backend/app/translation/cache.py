from __future__ import annotations
"""
LinguaChat — Translation Cache
Implementation: Moayad Al-Soufi — TASK-03-MOAYAD
Contract: docs/translation-contract.md § 4. Cache Contract

- Key format: translate:{source_lang}:{target_lang}:{sha256(text)}
- source_used = "cache" on HIT
- In-Memory fallback by default + optional Redis via REDIS_URL
- Non-fatal: failures never raise exceptions, always fall through to providers.
"""
import hashlib
import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


def _make_cache_key(source_lang: str, target_lang: str, text: str) -> str:
    """
    Builds the deterministic cache key according to the contract:
    translate:{source_lang}:{target_lang}:{sha256(text)}
    """
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"translate:{source_lang}:{target_lang}:{text_hash}"


# Alias matching skeleton
def _cache_key(text: str, source_lang: str, target_lang: str) -> str:
    """Alternative signature matching skeleton."""
    return _make_cache_key(source_lang, target_lang, text)


class TranslationCache:
    """
    Dual-layer translation cache:
    - In-Memory Dictionary (default and always available fallback).
    - Redis (optional — activated when REDIS_URL is configured and reachable).
    Never raises exceptions externally if cache fails.
    """

    DEFAULT_TTL = 3600  # 1 hour in seconds

    def __init__(self):
        # In-Memory store: {key: {"value": dict, "expires_at": float}}
        self._memory: dict = {}
        self._redis_client = None
        self._redis_available = False

    async def initialize(self) -> None:
        """
        Attempts connection to Redis if REDIS_URL is set in settings.
        Failures do not interrupt execution — smoothly falls back to in-memory cache.
        """
        try:
            from app.core.config import settings
            if settings.REDIS_URL:
                import redis.asyncio as aioredis
                self._redis_client = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                await self._redis_client.ping()
                self._redis_available = True
                logger.info("Connected to Redis translation cache successfully")
        except Exception:
            self._redis_available = False
            logger.info("Redis is unavailable — operating with in-memory translation cache")

    def _is_memory_expired(self, entry: dict) -> bool:
        """Check if an in-memory cache entry has exceeded its TTL."""
        return time.monotonic() > entry.get("expires_at", 0)

    async def get(
        self, source_lang: str, target_lang: str, text: str
    ) -> Optional[dict]:
        """
        Lookup cached translation.

        Returns:
            dict with source_used="cache" on HIT, or None on MISS.
        """
        key = _make_cache_key(source_lang, target_lang, text)

        # Try Redis first if available
        if self._redis_available and self._redis_client:
            try:
                raw = await self._redis_client.get(key)
                if raw:
                    cached_data = json.loads(raw)
                    return {
                        "translated_text": cached_data["translated_text"],
                        "source_used": "cache",
                        "confidence": cached_data.get("confidence"),
                    }
            except Exception:
                logger.debug("Failed reading from Redis — falling back to in-memory store")

        # In-Memory lookup
        entry = self._memory.get(key)
        if entry and not self._is_memory_expired(entry):
            data = entry["value"]
            return {
                "translated_text": data["translated_text"],
                "source_used": "cache",
                "confidence": data.get("confidence"),
            }

        return None  # Cache MISS

    async def set(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
        translated_text: str,
        original_source_used: str = "libretranslate",
        confidence: Optional[float] = None,
        ttl: int = DEFAULT_TTL,
    ) -> None:
        """
        Stores a translation result in cache.
        Does not raise exceptions on failure.
        """
        key = _make_cache_key(source_lang, target_lang, text)
        value = {
            "translated_text": translated_text,
            "original_source_used": original_source_used,
            "confidence": confidence,
            "cached_at": time.time(),
        }

        # Store in Redis if available
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.setex(key, ttl, json.dumps(value))
            except Exception:
                logger.debug("Failed writing to Redis — stored in in-memory cache instead")

        # Always store in In-Memory as reliable fallback
        self._memory[key] = {
            "value": value,
            "expires_at": time.monotonic() + ttl,
        }


# Global shared instance
translation_cache = TranslationCache()


# ─────────────────────────────────────────────
# Public Contract Functions (§ 4. Cache Contract)
# ─────────────────────────────────────────────

async def get_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[dict]:
    """
    Retrieve a cached translation result matching contract signature.
    Returns translation dict with source_used="cache", or None on cache miss.
    """
    try:
        return await translation_cache.get(source_lang, target_lang, text)
    except Exception:
        return None


async def set_cached_translation(
    text: str,
    source_lang: str,
    target_lang: str,
    translation: dict,
    ttl_seconds: int = 3600,
) -> None:
    """
    Store a translation result in cache with TTL matching contract signature.
    Must not raise if cache backend is unavailable.
    """
    try:
        translated_text = translation.get("translated_text", "")
        source_used = translation.get("source_used", "libretranslate")
        confidence = translation.get("confidence")

        await translation_cache.set(
            source_lang=source_lang,
            target_lang=target_lang,
            text=text,
            translated_text=translated_text,
            original_source_used=source_used,
            confidence=confidence,
            ttl=ttl_seconds,
        )
    except Exception:
        pass

