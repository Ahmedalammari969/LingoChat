"""
LinguaChat — Unit Tests for Translation Cache
Task: TASK-03-MOAYAD
Contract: docs/translation-contract.md § 4
"""
import hashlib
import pytest

from app.translation.cache import (
    TranslationCache,
    _make_cache_key,
    _cache_key,
    get_cached_translation,
    set_cached_translation,
    translation_cache,
)


class TestCacheKey:
    """Tests for cache key generation using SHA-256."""

    def test_key_format(self):
        """Cache key must strictly follow translate:{source}:{target}:{sha256}."""
        key = _make_cache_key("ar", "en", "مرحبا")
        assert key.startswith("translate:ar:en:")
        parts = key.split(":")
        assert len(parts) == 4

    def test_sha256_in_key(self):
        """Verify that the 4th part is a valid SHA-256 hex digest."""
        text = "Hello World"
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        key = _make_cache_key("en", "ar", text)
        assert key.endswith(expected_hash)
        assert _cache_key(text, "en", "ar") == key

    def test_different_texts_different_keys(self):
        """Distinct texts must yield distinct keys."""
        key1 = _make_cache_key("en", "ar", "Hello")
        key2 = _make_cache_key("en", "ar", "World")
        assert key1 != key2


class TestTranslationCache:
    """Tests for TranslationCache (In-Memory & Error-free behaviour)."""

    def setup_method(self):
        self.cache = TranslationCache()

    @pytest.mark.asyncio
    async def test_miss_returns_none(self):
        """Cache MISS must return None."""
        result = await self.cache.get("en", "ar", "not cached text")
        assert result is None

    @pytest.mark.asyncio
    async def test_hit_returns_cache_source(self):
        """Cache HIT must return dict with source_used='cache'."""
        await self.cache.set("en", "ar", "Hello", "مرحبا", "libretranslate", 0.95)
        result = await self.cache.get("en", "ar", "Hello")

        assert result is not None
        assert result["source_used"] == "cache"
        assert result["translated_text"] == "مرحبا"
        assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_source_used_is_always_cache(self):
        """source_used must ALWAYS be 'cache' on HIT, never 'google' or 'libretranslate'."""
        await self.cache.set("fr", "ar", "Bonjour", "مرحبا", "google", 0.90)
        result = await self.cache.get("fr", "ar", "Bonjour")

        assert result["source_used"] == "cache"
        assert result["source_used"] != "none"
        assert result["source_used"] != "google"

    @pytest.mark.asyncio
    async def test_different_target_langs_isolated(self):
        """Translations to different target languages must be stored in independent keys."""
        await self.cache.set("en", "ar", "Hello", "مرحبا", "libretranslate")
        await self.cache.set("en", "fr", "Hello", "Bonjour", "libretranslate")

        result_ar = await self.cache.get("en", "ar", "Hello")
        result_fr = await self.cache.get("en", "fr", "Hello")

        assert result_ar["translated_text"] == "مرحبا"
        assert result_fr["translated_text"] == "Bonjour"

    @pytest.mark.asyncio
    async def test_set_does_not_raise_on_empty(self):
        """set operation must never raise exceptions even on unexpected inputs."""
        try:
            await self.cache.set("xx", "yy", "", "empty", "libretranslate")
        except Exception as e:
            pytest.fail(f"set raised unexpected exception: {e}")

    @pytest.mark.asyncio
    async def test_module_level_contract_functions(self):
        """Test public module functions get_cached_translation & set_cached_translation."""
        trans_dict = {
            "translated_text": "صباح الخير",
            "source_used": "libretranslate",
            "confidence": 0.95,
        }
        await set_cached_translation("Good morning", "en", "ar", trans_dict, ttl_seconds=3600)
        cached = await get_cached_translation("Good morning", "en", "ar")

        assert cached is not None
        assert cached["translated_text"] == "صباح الخير"
        assert cached["source_used"] == "cache"
