"""
LinguaChat — Integration Tests for Translation Subsystem
Task: TASK-04-MOAYAD
Contract: docs/translation-contract.md
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.translation import (
    translate_message,
    detect_language,
    translation_cache,
    TranslationError,
)


class TestTranslationSubsystemIntegration:
    """End-to-end integration tests for detector, cache, providers, and service."""

    @pytest.mark.asyncio
    async def test_end_to_end_arabic_to_arabic_identity(self):
        """Arabic to Arabic flow returns identity without external calls."""
        res = await translate_message("أهلاً وسهلاً", "ar", "ar")
        assert res["translated_text"] == "أهلاً وسهلاً"
        assert res["source_used"] == "identity"
        assert res["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_end_to_end_auto_detect_translation_flow(self):
        """End-to-end flow with auto-detection and caching."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"translatedText": "Welcome to LinguaChat"}
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            # First call: Translates and populates cache
            res1 = await translate_message("مرحبا بك في لينجواتشات", "auto", "en")
            assert res1["translated_text"] == "Welcome to LinguaChat"
            assert res1["source_used"] == "libretranslate"

            # Second call: Served instantly from Cache
            res2 = await translate_message("مرحبا بك في لينجواتشات", "ar", "en")
            assert res2["translated_text"] == "Welcome to LinguaChat"
            assert res2["source_used"] == "cache"
