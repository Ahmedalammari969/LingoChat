"""
LinguaChat — Unit Tests for Language Detector
Task: TASK-01-MOAYAD
Contract: docs/translation-contract.md § 3
"""
import pytest
from app.translation.detector import detect_language


class TestDetectLanguage:
    """Test suite for detect_language function."""

    @pytest.mark.asyncio
    async def test_arabic_text(self):
        result = await detect_language("مرحبا بالعالم كيف حالك اليوم")
        assert result == "ar"

    @pytest.mark.asyncio
    async def test_english_text(self):
        result = await detect_language("Hello, World! This is a test message.")
        assert result == "en"

    @pytest.mark.asyncio
    async def test_french_text(self):
        result = await detect_language("Bonjour tout le monde, comment allez-vous?")
        assert result == "fr"

    @pytest.mark.asyncio
    async def test_spanish_text(self):
        result = await detect_language("Hola amigo, como estas hoy?")
        assert result == "es"

    @pytest.mark.asyncio
    async def test_german_text(self):
        result = await detect_language("Guten Tag, wie geht es Ihnen?")
        assert result == "de"

    @pytest.mark.asyncio
    async def test_empty_string(self):
        result = await detect_language("")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_whitespace_only(self):
        result = await detect_language("   \n\t  ")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_emojis_only(self):
        result = await detect_language("😀🎉🔥🚀❤️")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_symbols_only(self):
        result = await detect_language("!@#$%^&*()_+=-~`{}[]|:;'<>,.?/")
        assert result == "unknown"

    @pytest.mark.asyncio
    async def test_numbers_only(self):
        result = await detect_language("1234567890 987654321")
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
    async def test_never_raises_exception_on_invalid_inputs(self):
        invalid_inputs = [None, 12345, 3.14, True, [], {}, b"byte string", "\x00\x01\x02", "???"]
        for inp in invalid_inputs:
            try:
                result = await detect_language(inp)
                assert isinstance(result, str)
                assert result == "unknown" or len(result) >= 2
            except Exception as e:
                pytest.fail(f"detect_language raised an unexpected exception: {e}")
