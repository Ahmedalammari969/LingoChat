from __future__ import annotations
"""
LinguaChat — Translation Service (Skeleton)

PUBLIC INTERFACE for translation. This is the ONLY entry point consumers should use.
Implementation: Moayad Al-Soufi — TASK: Translation Service
See: docs/translation-contract.md
"""

from app.core.errors import TranslationError


async def translate_message(
    text: str,
    source_lang: str,
    target_lang: str,
) -> dict:
    """
    Translate text from source_lang to target_lang.

    This is the ONLY function consumers (WebSocket, Messages) should call.
    Do NOT call providers.py directly from outside this module.

    Args:
        text:        Non-empty text to translate.
        source_lang: ISO 639-1 code, or "auto" to trigger detection.
        target_lang: ISO 639-1 code of desired output language.

    Returns:
        {
            "translated_text": str,
            "source_used": "libretranslate" | "google" | "cache" | "identity",
            "confidence": float | None
        }

    Raises:
        TranslationError: If all providers fail and no cache entry exists.

    Implementation flow:
    1. If source_lang == "auto": call detector.detect_language(text)
    2. If source_lang == target_lang:
         → Return {"translated_text": text, "source_used": "identity", "confidence": 1.0}
         → Do NOT call any provider. The Gateway MUST NOT know about this shortcut.
    3. Check cache: cache.get_cached_translation(text, source_lang, target_lang)
    4. Try primary provider: LibreTranslateProvider
    5. If LibreTranslate fails AND GOOGLE_TRANSLATE_API_KEY is configured:
         → Try GoogleTranslateProvider
    6. If all active providers fail: raise TranslationError
    7. Cache successful result before returning (step 4 or 5 result)

    See: docs/translation-contract.md § 5. Translation Flow
    """
    raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")
