"""
backend/tests/translation/test_translation_cache.py
TASK-05: اختبارات طبقة الكاش
"""
import hashlib
import pytest
from app.translation.cache import TranslationCache, _make_cache_key


class TestCacheKey:
    """اختبارات توليد مفتاح الكاش."""

    def test_key_format(self):
        """المفتاح بصيغة translate:{source}:{target}:{sha256}."""
        key = _make_cache_key("ar", "en", "مرحبا")
        assert key.startswith("translate:ar:en:")
        parts = key.split(":")
        assert len(parts) == 4

    def test_sha256_in_key(self):
        """يتحقق أن الجزء الأخير هو SHA-256 صحيح."""
        text = "Hello World"
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        key = _make_cache_key("en", "ar", text)
        assert key.endswith(expected_hash)

    def test_different_texts_different_keys(self):
        """نصوص مختلفة تُنتج مفاتيح مختلفة."""
        key1 = _make_cache_key("en", "ar", "Hello")
        key2 = _make_cache_key("en", "ar", "World")
        assert key1 != key2


class TestTranslationCache:
    """اختبارات TranslationCache (In-Memory فقط)."""

    def setup_method(self):
        self.cache = TranslationCache()

    @pytest.mark.asyncio
    async def test_miss_returns_none(self):
        """MISS → يُرجع None."""
        result = await self.cache.get("en", "ar", "not cached text")
        assert result is None

    @pytest.mark.asyncio
    async def test_hit_returns_cache_source(self):
        """HIT → source_used='cache' إلزامياً."""
        await self.cache.set("en", "ar", "Hello", "مرحبا", "libretranslate", 0.95)
        result = await self.cache.get("en", "ar", "Hello")

        assert result is not None
        assert result["source_used"] == "cache"
        assert result["translated_text"] == "مرحبا"

    @pytest.mark.asyncio
    async def test_source_used_is_always_cache(self):
        """source_used = 'cache' دائماً عند الـ HIT — يُحظر أي قيمة أخرى."""
        await self.cache.set("fr", "ar", "Bonjour", "مرحبا", "google", 0.90)
        result = await self.cache.get("fr", "ar", "Bonjour")

        assert result["source_used"] == "cache"
        assert result["source_used"] != "none"
        assert result["source_used"] != "google"

    @pytest.mark.asyncio
    async def test_different_target_langs_isolated(self):
        """لغات هدف مختلفة → مفاتيح مستقلة."""
        await self.cache.set("en", "ar", "Hello", "مرحبا", "libretranslate")
        await self.cache.set("en", "fr", "Hello", "Bonjour", "libretranslate")

        result_ar = await self.cache.get("en", "ar", "Hello")
        result_fr = await self.cache.get("en", "fr", "Hello")

        assert result_ar["translated_text"] == "مرحبا"
        assert result_fr["translated_text"] == "Bonjour"

    @pytest.mark.asyncio
    async def test_set_does_not_raise(self):
        """set لا يرفع أي استثناء حتى عند إدخالات غريبة."""
        try:
            await self.cache.set("xx", "yy", "", "empty", "libretranslate")
        except Exception as e:
            pytest.fail(f"set رفعت استثناءً: {e}")
