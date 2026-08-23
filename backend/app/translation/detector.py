"""
LinguaChat — Language Detector
Implementation: Moayad Al-Soufi — TASK-01-MOAYAD
Contract: docs/translation-contract.md § 3. Language Detection Contract

- Returns ISO 639-1 language code (e.g., "ar", "en", "fr").
- Returns "unknown" on failure, empty text, symbols, or emojis.
- NEVER raises an exception.
"""
import logging
import unicodedata

logger = logging.getLogger(__name__)

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False
    logger.warning("langdetect is not available — detect_language will return 'unknown'")


def _has_letters(text: str) -> bool:
    """
    Check if the text contains at least one alphabetic letter character.
    Returns False if text consists only of digits, symbols, or emojis.
    """
    return any(unicodedata.category(c).startswith("L") for c in text)


async def detect_language(text: str) -> str:
    """
    Detect the language of provided text.

    Args:
        text: Raw text to analyze.

    Returns:
        ISO 639-1 language code (e.g., "ar", "en", "fr").
        Returns "unknown" if detection fails — NEVER raises an exception.
    """
    try:
        # Validate non-empty string input
        if not text or not isinstance(text, str) or not text.strip():
            return "unknown"

        stripped = text.strip()

        # Reject texts containing no linguistic letters (numbers only, emojis, symbols)
        if not _has_letters(stripped):
            return "unknown"

        # If langdetect library is unavailable, return unknown safely
        if not _LANGDETECT_AVAILABLE:
            return "unknown"

        detected = detect(stripped)

        # Validate ISO 639-1 format (2-3 lowercase characters)
        if detected and isinstance(detected, str) and 2 <= len(detected) <= 3:
            return detected.lower()

        return "unknown"

    except Exception:
        # Strictly catch all exceptions to prevent crashes — NEVER raise
        logger.debug("Language detection failed or returned no features — returning 'unknown'", exc_info=False)
        return "unknown"

