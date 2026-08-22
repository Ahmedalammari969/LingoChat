"""
backend/tests/translation/test_translation_service.py
TASK-08: اختبارات خدمة الترجمة الموحدة translate_message
"""
from unittest.mock import PropertyMock
import pytest
import app.translation.service
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from app.translation.service import translate_message
from app.translation.errors import TranslationError


class TestTranslateMessageFlow:

    @pytest.mark.asyncio
    async def test_identity_shortcut(self):
        result = await translate_message("Hello", "en", "en")
        assert result["source_used"] == "identity"
        assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        cached_result = {
            "translated_text": "مرحبا",
            "source_used": "cache",
            "confidence": 0.95,
        }
        with patch(
            "app.translation.service.translation_cache.get",
            new=AsyncMock(return_value=cached_result)
        ):
            result = await translate_message("Hello", "en", "ar")
        assert result["source_used"] == "cache"
        assert result["translated_text"] == "مرحبا"

    @pytest.mark.asyncio
    async def test_libretranslate_success(self):
        libre_result = {
            "translated_text": "مرحبا",
            "source_used": "libretranslate",
            "confidence": 0.95,
        }
        with patch(
            "app.translation.service.translation_cache.get",
            new=AsyncMock(return_value=None)
        ), patch(
            "app.translation.service.translation_cache.set",
            new=AsyncMock()
        ), patch.object(
            type(app.translation.service._libre_provider),
            "is_available",
            new_callable=PropertyMock,
            return_value=True
        ), patch(
            "app.translation.service._libre_provider.translate",
            new=AsyncMock(return_value=libre_result)
        ):
            result = await translate_message("Hello", "en", "ar")
        assert result["source_used"] == "libretranslate"

    @pytest.mark.asyncio
    async def test_google_fallback_when_libre_fails(self):
        from app.translation.errors import ProviderError
        import app.translation.service as svc

        google_result = {
            "translated_text": "مرحبا",
            "source_used": "google",
            "confidence": 0.90,
        }
        with patch(
            "app.translation.service.translation_cache.get",
            new=AsyncMock(return_value=None)
        ), patch(
            "app.translation.service.translation_cache.set",
            new=AsyncMock()
        ), patch.object(
            type(svc._libre_provider), "is_available",
            new_callable=PropertyMock, return_value=True
        ), patch(
            "app.translation.service._libre_provider.translate",
            new=AsyncMock(side_effect=ProviderError("libretranslate", "down"))
        ), patch.object(
            type(svc._google_provider), "is_available",
            new_callable=PropertyMock, return_value=True
        ), patch(
            "app.translation.service._google_provider.translate",
            new=AsyncMock(return_value=google_result)
        ):
            result = await translate_message("Hello", "en", "ar")
        assert result["source_used"] == "google"

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_translation_error(self):
        import app.translation.service as svc
        with patch(
            "app.translation.service.translation_cache.get",
            new=AsyncMock(return_value=None)
        ), patch.object(
            type(svc._libre_provider), "is_available",
            new_callable=PropertyMock, return_value=False
        ), patch.object(
            type(svc._google_provider), "is_available",
            new_callable=PropertyMock, return_value=False
        ):
            with pytest.raises(TranslationError):
                await translate_message("Hello", "en", "ar")

    @pytest.mark.asyncio
    async def test_auto_detect_then_identity(self):
        with patch(
            "app.translation.service.detect_language",
            new=AsyncMock(return_value="ar")
        ):
            result = await translate_message("مرحبا", "auto", "ar")
        assert result["source_used"] == "identity"

    @pytest.mark.asyncio
    async def test_source_used_never_none(self):
        result = await translate_message("مرحبا", "ar", "ar")
        assert result["source_used"] != "none"
