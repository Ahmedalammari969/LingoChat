"""
LinguaChat — Unit Tests for Translation Providers
Task: TASK-02-MOAYAD
Contract: docs/translation-contract.md § 6 & § 7
"""
import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock

from app.translation.providers import (
    TranslationProvider,
    BaseTranslationProvider,
    LibreTranslateProvider,
    GoogleTranslateProvider,
    ProviderError,
)
from app.core.config import settings


class TestLibreTranslateProvider:
    """Tests for LibreTranslateProvider (Primary Local AI / Remote Provider)."""

    @pytest.mark.asyncio
    async def test_successful_translation(self):
        provider = LibreTranslateProvider()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": "Hello world"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await provider.translate("مرحبا بالعالم", "ar", "en")

            assert result["translated_text"] == "Hello world"
            assert result["source_used"] == "libretranslate"
            assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_http_error_raises_provider_error(self):
        provider = LibreTranslateProvider()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Internal Server Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_post.return_value = mock_response

            with pytest.raises(ProviderError) as exc_info:
                await provider.translate("مرحبا", "ar", "en")

            assert exc_info.value.provider == "libretranslate"
            assert "HTTP error 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_timeout_raises_provider_error(self):
        provider = LibreTranslateProvider()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Connection timed out")

            with pytest.raises(ProviderError) as exc_info:
                await provider.translate("مرحبا", "ar", "en")

            assert exc_info.value.provider == "libretranslate"
            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_translation_response_raises_provider_error(self):
        provider = LibreTranslateProvider()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": ""}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            with pytest.raises(ProviderError) as exc_info:
                await provider.translate("مرحبا", "ar", "en")

            assert exc_info.value.provider == "libretranslate"

    @pytest.mark.asyncio
    async def test_unavailable_when_url_empty(self):
        provider = LibreTranslateProvider()
        provider.url = ""

        with pytest.raises(ProviderError) as exc_info:
            await provider.translate("مرحبا", "ar", "en")

        assert exc_info.value.provider == "libretranslate"


class TestGoogleTranslateProvider:
    """Tests for GoogleTranslateProvider (Optional Fallback)."""

    @pytest.mark.asyncio
    async def test_skipped_when_api_key_missing(self):
        provider = GoogleTranslateProvider()
        provider.api_key = ""

        assert provider.is_available is False
        assert provider.is_configured() is False

        with pytest.raises(ProviderError) as exc_info:
            await provider.translate("مرحبا", "ar", "en")

        assert exc_info.value.provider == "google"
        assert "not set" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_successful_translation_with_api_key(self):
        provider = GoogleTranslateProvider()
        provider.api_key = "mock-google-key"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "translations": [
                    {"translatedText": "Hello from Google"}
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await provider.translate("مرحبا", "ar", "en")

            assert result["translated_text"] == "Hello from Google"
            assert result["source_used"] == "google"
            assert result["confidence"] == 0.90

    @pytest.mark.asyncio
    async def test_google_timeout_raises_provider_error(self):
        provider = GoogleTranslateProvider()
        provider.api_key = "mock-google-key"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Google timed out")

            with pytest.raises(ProviderError) as exc_info:
                await provider.translate("مرحبا", "ar", "en")

            assert exc_info.value.provider == "google"
            assert "timed out" in str(exc_info.value)
