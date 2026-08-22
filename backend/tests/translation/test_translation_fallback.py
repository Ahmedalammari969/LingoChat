"""
backend/tests/translation/test_translation_fallback.py
TASK-04: اختبارات GoogleTranslateProvider (المزود الاحتياطي الاختياري)
"""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from app.translation.providers import GoogleTranslateProvider
from app.translation.errors import ProviderError


class TestGoogleTranslateProvider:
    def setup_method(self):
        self.provider = GoogleTranslateProvider()

    def test_not_available_without_key(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = ""
            assert self.provider.is_available is False

    def test_available_with_key(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = "test-api-key-123"
            assert self.provider.is_available is True

    @pytest.mark.asyncio
    async def test_raises_provider_error_without_key(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = ""
            with pytest.raises(ProviderError) as exc_info:
                await self.provider.translate("test", "en", "ar")
        assert exc_info.value.provider_name == "google"

    @pytest.mark.asyncio
    async def test_successful_translation(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"translations": [{"translatedText": "مرحبا"}]}
        }
        mock_response.raise_for_status = MagicMock()

        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = "test-key"
            mock_settings.LIBRETRANSLATE_URL = ""
            mock_settings.LIBRETRANSLATE_API_KEY = ""

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_cls.return_value = mock_client

                result = await self.provider.translate("Hello", "en", "ar")

        assert result["source_used"] == "google"
        assert result["translated_text"] == "مرحبا"
        assert result["confidence"] == 0.90

    @pytest.mark.asyncio
    async def test_google_timeout_raises_provider_error(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = "test-key"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.post = AsyncMock(
                    side_effect=httpx.TimeoutException("timeout")
                )
                mock_client_cls.return_value = mock_client

                with pytest.raises(ProviderError):
                    await self.provider.translate("test", "en", "ar")

    def test_google_is_optional_not_mandatory(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.GOOGLE_TRANSLATE_API_KEY = ""
            assert self.provider.is_available is False
