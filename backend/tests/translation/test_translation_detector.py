"""
backend/tests/translation/test_translation_detector.py
TASK-02: اختبارات كاشف اللغات
معيار: لا يُرفع أي استثناء — دائماً يُرجع string صالح
"""
import pytest
from app.translation.detector import detect_language


class TestDetectLanguage:
    """اختبارات دالة detect_language."""

    @pytest.mark.asyncio
    async def test_arabic_text(self):
        result = await detect_language("مرحبا بالعالم")
        assert result == "ar"

    @pytest.mark.asyncio
    async def test_english_text(self):
        result = await detect_language("Hello, World!")
        assert result == "en"

    @pytest.mark.asyncio
    async def test_french_text(self):
        result = await detect_language("Bonjour le monde")
        assert result == "fr"

    @pytest.mark.asyncio
    async def test_empty_string(self):
        result = await detect_language("")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_whitespace_only(self):
        result = await detect_language("   ")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_emojis_only(self):
        result = await detect_language("😀🎉🔥")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_symbols_only(self):
        result = await detect_language("!@#$%^&*()")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_returns_lowercase(self):
        result = await detect_language("Hello World")
        assert result == result.lower()

    @pytest.mark.asyncio
    async def test_returns_string(self):
        result = await detect_language("مرحبا")
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_never_raises_exception(self):
        inputs = [None.__class__.__name__, "???", "\x00\x01\x02", "123"]
        for inp in inputs:
            try:
                result = await detect_language(inp)
                assert isinstance(result, str)
            except Exception as e:
                pytest.fail(f"detect_language رفعت استثناءً غير مسموح به: {e}")
