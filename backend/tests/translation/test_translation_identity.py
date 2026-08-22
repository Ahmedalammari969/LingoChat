"""
backend/tests/translation/test_translation_identity.py
TASK-06: اختبارات قاعدة Identity الإلزامية
"""
import pytest
from unittest.mock import AsyncMock, patch
from app.translation.service import translate_message


class TestIdentityRule:
    @pytest.mark.asyncio
    async def test_same_language_returns_identity(self):
        result = await translate_message("مرحبا", "ar", "ar")
        assert result["source_used"] == "identity"
        assert result["translated_text"] == "مرحبا"
        assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_english_to_english_identity(self):
        result = await translate_message("Hello", "en", "en")
        assert result["source_used"] == "identity"

    @pytest.mark.asyncio
    async def test_identity_never_returns_none(self):
        result = await translate_message("test", "fr", "fr")
        assert result["source_used"] != "none"
        assert result["source_used"] == "identity"

    @pytest.mark.asyncio
    async def test_identity_confidence_is_1(self):
        result = await translate_message("مرحبا", "ar", "ar")
        assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_identity_returns_original_text(self):
        original = "مرحبا بالعالم 123!"
        result = await translate_message(original, "ar", "ar")
        assert result["translated_text"] == original

    @pytest.mark.asyncio
    async def test_identity_does_not_call_providers(self):
        with patch("app.translation.service._libre_provider.translate") as mock_libre, \
             patch("app.translation.service._google_provider.translate") as mock_google:
            mock_libre = AsyncMock()
            mock_google = AsyncMock()
            result = await translate_message("test", "en", "en")
        mock_libre.assert_not_called()
        mock_google.assert_not_called()
        assert result["source_used"] == "identity"
