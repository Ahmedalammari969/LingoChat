from __future__ import annotations
"""
LinguaChat — Translation Service
Implementation: Moayad Al-Soufi — TASK-04-MOAYAD
Contract: docs/translation-contract.md § 2. Primary Function Contract & § 5. Translation Flow

PUBLIC INTERFACE for translation. This is the ONLY entry point consumers should use.
Architecture Flow:
1. Auto Detect (if source_lang == 'auto')
2. Identity check (source_lang == target_lang -> source_used="identity", confidence=1.0)
3. Cache lookup (HIT -> source_used="cache")
4. Primary Provider (LibreTranslate local AI model / API)
5. Fallback Provider (Google Cloud Translation API, optional)
6. Error handling (Raise TranslationError if all fail)
"""
import logging
from typing import Optional

from app.core.errors import TranslationError
from app.translation.detector import detect_language
from app.translation.cache import translation_cache
from app.translation.providers import (
    ProviderError,
    LibreTranslateProvider,
    GoogleTranslateProvider,
)

logger = logging.getLogger(__name__)

# Provider instances (shared throughout application lifecycle)
_libre_provider = LibreTranslateProvider()
_google_provider = GoogleTranslateProvider()


async def translate_message(
    text: str,
    source_lang: str,
    target_lang: str,
) -> dict:
    """
    Translate text from source_lang to target_lang.
    The ONLY public translation function called by WebSocket and REST API.

    Args:
        text: Non-empty text content to translate.
        source_lang: ISO 639-1 code (e.g., 'ar', 'en'), or 'auto' for automatic detection.
        target_lang: ISO 639-1 code of desired output language.

    Returns:
        {
            "translated_text": str,
            "source_used": "libretranslate" | "google" | "cache" | "identity",
            "confidence": float | None
        }

    Raises:
        TranslationError: If all providers fail and no cache entry exists.
    """
    if not text:
        return {
            "translated_text": "",
            "source_used": "identity",
            "confidence": 1.0,
        }

    effective_source = source_lang.strip().lower() if source_lang else "auto"
    target = target_lang.strip().lower() if target_lang else "en"

    # ──────────────────────────────────────────────────
    # Step 1: Automatic Language Detection (if 'auto')
    # ──────────────────────────────────────────────────
    if effective_source == "auto":
        detected = await detect_language(text)
        if detected and detected != "unknown":
            effective_source = detected.lower()
            logger.debug("Language detected automatically: '%s'", effective_source)
        else:
            effective_source = "auto"
            logger.debug("Language detection returned 'unknown'")

    # ──────────────────────────────────────────────────
    # Step 2: Identity Rule (source == target)
    # MUST return source_used="identity" and confidence=1.0
    # NEVER returns 'none'
    # ──────────────────────────────────────────────────
    if effective_source == target:
        logger.debug("Identity match: source '%s' == target '%s'", effective_source, target)
        return {
            "translated_text": text,
            "source_used": "identity",
            "confidence": 1.0,
        }

    # ──────────────────────────────────────────────────
    # Step 3: Cache Lookup
    # ──────────────────────────────────────────────────
    if effective_source != "auto":
        cached = await translation_cache.get(effective_source, target, text)
        if cached is not None:
            logger.debug("Translation cache HIT: %s -> %s", effective_source, target)
            return cached

    # ──────────────────────────────────────────────────
    # Step 4: Primary Provider (LibreTranslate Local AI)
    # ──────────────────────────────────────────────────
    result = await _try_provider(_libre_provider, text, effective_source, target)
    if result:
        await _store_in_cache(effective_source, target, text, result)
        return result

    # ──────────────────────────────────────────────────
    # Step 5: Fallback Provider (Google Translate - Optional)
    # ──────────────────────────────────────────────────
    result = await _try_provider(_google_provider, text, effective_source, target)
    if result:
        await _store_in_cache(effective_source, target, text, result)
        return result

    # ──────────────────────────────────────────────────
    # Step 6: All Providers Failed
    # ──────────────────────────────────────────────────
    logger.error("All translation providers failed for '%s' -> '%s'", effective_source, target)
    raise TranslationError(f"All translation providers failed for '{effective_source}' to '{target}'")


async def _try_provider(
    provider,
    text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[dict]:
    """
    Attempt translation with a single provider.
    Returns translation dict on success, or None on failure (enabling fallback).
    """
    if not provider.is_available:
        return None

    try:
        return await provider.translate(text, source_lang, target_lang)
    except ProviderError as e:
        prov = getattr(e, "provider", "unknown")
        msg = getattr(e, "message", str(e))
        logger.warning("Provider '%s' failed: %s", prov, msg)
        return None
    except Exception as e:
        logger.error("Unexpected error in translation provider: %s", e)
        return None


async def _store_in_cache(
    source_lang: str,
    target_lang: str,
    text: str,
    result: dict,
) -> None:
    """Store translation in cache without raising exceptions."""
    if source_lang == "auto":
        return
    try:
        await translation_cache.set(
            source_lang=source_lang,
            target_lang=target_lang,
            text=text,
            translated_text=result.get("translated_text", ""),
            original_source_used=result.get("source_used", "libretranslate"),
            confidence=result.get("confidence"),
        )
    except Exception:
        logger.debug("Failed saving translation to cache (non-fatal)", exc_info=False)

