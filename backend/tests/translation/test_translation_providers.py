"""
backend/tests/translation/test_translation_providers.py
TASK-03: اختبارات LibreTranslateProvider
"""
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from app.translation.providers import LibreTranslateProvider
from app.translation.errors import ProviderError


class TestLibreTranslateProvider:
    def setup_method(self):
        self.provider = LibreTranslateProvider()

    @pytest.mark.asyncio
    async def test_successful_translation(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": "Hello"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await self.provider.translate("مرحبا", "ar", "en")

        assert result["source_used"] == "libretranslate"
        assert result["translated_text"] == "Hello"
        assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_timeout_raises_provider_error(self):
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client_cls.return_value = mock_client

            with pytest.raises(ProviderError) as exc_info:
                await self.provider.translate("test", "en", "ar")

        assert exc_info.value.provider_name == "libretranslate"

    @pytest.mark.asyncio
    async def test_http_error_raises_provider_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            with pytest.raises(ProviderError):
                await self.provider.translate("test", "en", "ar")

    @pytest.mark.asyncio
    async def test_missing_translated_text_raises_provider_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            with pytest.raises(ProviderError):
                await self.provider.translate("test", "en", "ar")

    def test_is_available_with_url(self):
        with patch("app.translation.providers.settings") as mock_settings:
            mock_settings.LIBRETRANSLATE_URL = "http://localhost:5000"
            mock_settings.LIBRETRANSLATE_API_KEY = ""
            assert self.provider.is_available is True
