"""
LinguaChat — Unit Tests for Unified Translation Service
Task: TASK-04-MOAYAD
Contract: docs/translation-contract.md § 2 & § 5
"""
import pytest
from unittest.mock import patch, AsyncMock

from app.translation.service import translate_message
from app.translation.cache import translation_cache
from app.translation.providers import ProviderError
from app.core.errors import TranslationError


class TestTranslateMessageService:
    """Test suite for unified translate_message function."""

    def setup_method(self):
        """Reset in-memory cache before each test run."""
        translation_cache._memory.clear()

    @pytest.mark.asyncio
    async def test_identity_rule_same_languages(self):
        """When source_lang == target_lang, return immediately with source_used='identity'."""
        result = await translate_message("مرحبا بالعالم", "ar", "ar")

        assert result["translated_text"] == "مرحبا بالعالم"
        assert result["source_used"] == "identity"
        assert result["confidence"] == 1.0
        assert result["source_used"] != "none"

    @pytest.mark.asyncio
    async def test_identity_rule_case_insensitive(self):
        """Identity check must be case-insensitive (e.g., 'EN' == 'en')."""
        result = await translate_message("Hello world", "EN", "en")

        assert result["translated_text"] == "Hello world"
        assert result["source_used"] == "identity"
        assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_auto_detect_triggers_identity(self):
        """Auto-detected language matching target_lang triggers identity rule."""
        with patch("app.translation.service.detect_language", new_callable=AsyncMock) as mock_detect:
            mock_detect.return_value = "ar"
            result = await translate_message("السلام عليكم", "auto", "ar")

            assert result["translated_text"] == "السلام عليكم"
            assert result["source_used"] == "identity"
            assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_cache_hit_returns_cached_result(self):
        """When translation is in cache, return cache result directly."""
        await translation_cache.set("ar", "en", "شكرا", "Thank you", "libretranslate", 0.95)
        result = await translate_message("شكرا", "ar", "en")

        assert result["translated_text"] == "Thank you"
        assert result["source_used"] == "cache"

    @pytest.mark.asyncio
    async def test_primary_provider_success(self):
        """Primary provider (LibreTranslate) handles translation and saves to cache."""
        mock_res = {
            "translated_text": "Good morning",
            "source_used": "libretranslate",
            "confidence": 0.95,
        }

        with patch("app.translation.service._try_provider", new_callable=AsyncMock) as mock_try:
            mock_try.side_effect = [mock_res, None]
            result = await translate_message("صباح الخير يا صديقي", "ar", "en")

            assert result["translated_text"] == "Good morning"
            assert result["source_used"] == "libretranslate"
            assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_fallback_provider_when_primary_fails(self):
        """When LibreTranslate fails, fallback to GoogleTranslateProvider."""
        google_res = {
            "translated_text": "Good evening",
            "source_used": "google",
            "confidence": 0.90,
        }

        with patch("app.translation.service._try_provider", new_callable=AsyncMock) as mock_try:
            mock_try.side_effect = [None, google_res]
            result = await translate_message("مساء الخير يا قوم", "ar", "en")

            assert result["translated_text"] == "Good evening"
            assert result["source_used"] == "google"
            assert result["confidence"] == 0.90

    @pytest.mark.asyncio
    async def test_all_providers_failed_raises_translation_error(self):
        """When all providers fail, TranslationError must be raised."""
        with patch("app.translation.service._try_provider", new_callable=AsyncMock) as mock_try:
            mock_try.return_value = None

            with pytest.raises(TranslationError) as exc_info:
                await translate_message("نص غير قابل للترجمة مطلقاً", "ar", "zh")

            assert "All translation providers failed" in str(exc_info.value)
