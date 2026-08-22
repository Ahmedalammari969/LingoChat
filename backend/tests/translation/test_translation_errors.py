"""
backend/tests/translation/test_translation_errors.py
TASK-07: اختبارات استثناءات الترجمة
"""
import pytest
from app.translation.errors import TranslationError, ProviderError


class TestProviderError:
    def test_provider_error_has_provider_name(self):
        err = ProviderError("libretranslate", "timeout")
        assert err.provider_name == "libretranslate"

    def test_provider_error_has_reason(self):
        err = ProviderError("google", "HTTP 500")
        assert err.reason == "HTTP 500"

    def test_provider_error_is_exception(self):
        assert issubclass(ProviderError, Exception)

    def test_provider_error_message_format(self):
        err = ProviderError("libretranslate", "connection refused")
        assert "libretranslate" in str(err)


class TestTranslationError:
    def test_translation_error_is_exception(self):
        assert issubclass(TranslationError, Exception)

    def test_translation_error_default_message(self):
        err = TranslationError()
        assert err.message
        assert len(err.message) > 0

    def test_translation_error_custom_message(self):
        err = TranslationError("فشل كل شيء")
        assert err.message == "فشل كل شيء"

    def test_translation_error_not_provider_error(self):
        assert not issubclass(TranslationError, ProviderError)
        assert not issubclass(ProviderError, TranslationError)

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_translation_error(self):
        from unittest.mock import patch, AsyncMock, PropertyMock
        from app.translation.service import translate_message
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
