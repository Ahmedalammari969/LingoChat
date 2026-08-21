from __future__ import annotations
"""
LinguaChat — Translation Providers (Skeleton)

Implements the TranslationProvider interface for LibreTranslate and Google.
Implementation: Moayad Al-Soufi — TASK: Translation Service
See: docs/translation-contract.md § 6. Provider Interface

ARCHITECTURE FREEZE (2026-08-13):
- Primary provider: LibreTranslate (always required)
- Fallback provider: Google Cloud Translation API (optional)
  Active only when GOOGLE_TRANSLATE_API_KEY is set in environment.
  If key is absent, GoogleTranslateProvider MUST be skipped silently.

DO NOT import this file directly from outside the translation module.
Use translation/service.py instead.
"""

from abc import ABC, abstractmethod
from app.core.config import settings


class ProviderError(Exception):
    """Raised by a specific provider on failure."""
    pass


class TranslationProvider(ABC):
    """
    Abstract interface for translation providers.
    All providers MUST implement the translate() method.
    See: docs/translation-contract.md § 6. Provider Interface
    """

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> dict:
        """
        Returns:
            {
                "translated_text": str,
                "source_used": str,
                "confidence": float | None
            }
        Raises:
            ProviderError: On any failure.
        """
        ...


class LibreTranslateProvider(TranslationProvider):
    """
    Primary translation provider using LibreTranslate.
    URL configured via LIBRETRANSLATE_URL env var.
    See: docs/translation-contract.md
    Implementation: Moayad Al-Soufi
    """

    def __init__(self):
        self.url = settings.LIBRETRANSLATE_URL
        self.api_key = settings.LIBRETRANSLATE_API_KEY

    async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")


class GoogleTranslateProvider(TranslationProvider):
    """
    Optional fallback translation provider using Google Cloud Translation API.
    ACTIVE ONLY when GOOGLE_TRANSLATE_API_KEY environment variable is set.
    If the key is not configured, this provider MUST be skipped silently.

    source_used value: "google"
    See: docs/translation-contract.md § 6. Provider Interface
    Implementation: Moayad Al-Soufi

    RULES:
    - Never hardcode the API key.
    - Read from settings.GOOGLE_TRANSLATE_API_KEY only.
    - If settings.GOOGLE_TRANSLATE_API_KEY is empty/None: raise ProviderError immediately
      so the service layer knows to skip this provider.
    """

    def __init__(self):
        self.api_key = settings.GOOGLE_TRANSLATE_API_KEY

    def is_configured(self) -> bool:
        """Return True only if the API key is present."""
        return bool(self.api_key)

    async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        raise NotImplementedError("Implement in translation task — Moayad Al-Soufi")
