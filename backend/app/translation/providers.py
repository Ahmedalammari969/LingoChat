from __future__ import annotations
"""
LinguaChat — Translation Providers
Implementation: Moayad Al-Soufi — TASK-02-MOAYAD
Contract: docs/translation-contract.md § 6. Provider Interface & § 7. Error Handling

- Primary provider: LibreTranslate (local AI model / server at LIBRETRANSLATE_URL)
- Fallback provider: Google Cloud Translation API (optional, skipped if key is missing)
"""
import logging
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────

class ProviderError(Exception):
    """Raised by a specific provider on failure."""

    def __init__(self, provider: str, message: str = ""):
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}" if message else f"[{provider}] Provider failure")


# ─────────────────────────────────────────────
# Abstract Base Interface
# ─────────────────────────────────────────────

class TranslationProvider(ABC):
    """
    Abstract interface for translation providers.
    All providers MUST implement the translate() method.
    See: docs/translation-contract.md § 6. Provider Interface
    """

    @abstractmethod
    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        Translates text from source_lang to target_lang.

        Returns:
            {
                "translated_text": str,
                "source_used": str,   # e.g., "libretranslate" | "google"
                "confidence": float | None
            }
        Raises:
            ProviderError: On any failure.
        """
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured and available."""
        ...


# Alias for backward compatibility if referenced
BaseTranslationProvider = TranslationProvider


# ─────────────────────────────────────────────
# Primary Provider: LibreTranslate
# ─────────────────────────────────────────────

class LibreTranslateProvider(TranslationProvider):
    """
    Primary translation provider using LibreTranslate (Local AI Model / API).
    Configured via settings.LIBRETRANSLATE_URL (default: http://localhost:5000).
    Timeout is set to 10.0 seconds according to TRANSLATION_CONTRACT.
    """

    SOURCE_USED = "libretranslate"
    CONFIDENCE = 0.95
    TIMEOUT = 10.0

    def __init__(self):
        self.url = settings.LIBRETRANSLATE_URL or "http://localhost:5000"
        self.api_key = settings.LIBRETRANSLATE_API_KEY

    @property
    def is_available(self) -> bool:
        """Returns True if LIBRETRANSLATE_URL is configured."""
        return bool(self.url)

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        Sends translation request to LibreTranslate local model or API.

        Raises:
            ProviderError: On connection failure, HTTP error, timeout, or missing translation.
        """
        if not self.is_available:
            raise ProviderError(self.SOURCE_USED, "LIBRETRANSLATE_URL is not configured")

        url = f"{self.url.rstrip('/')}/translate"
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }

        if self.api_key:
            payload["api_key"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                translated = data.get("translatedText")
                if not translated:
                    raise ProviderError(
                        self.SOURCE_USED,
                        "Response did not contain 'translatedText'"
                    )

                return {
                    "translated_text": translated,
                    "source_used": self.SOURCE_USED,
                    "confidence": self.CONFIDENCE,
                }

        except httpx.TimeoutException as e:
            raise ProviderError(self.SOURCE_USED, f"Request timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                self.SOURCE_USED,
                f"HTTP error {e.response.status_code}"
            ) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.SOURCE_USED, f"Unexpected error: {e}") from e


# ─────────────────────────────────────────────
# Fallback Provider: Google Translate (Optional)
# ─────────────────────────────────────────────

class GoogleTranslateProvider(TranslationProvider):
    """
    Optional fallback translation provider using Google Cloud Translation API.
    Active only when GOOGLE_TRANSLATE_API_KEY is configured.
    Silently skipped if key is absent.
    """

    SOURCE_USED = "google"
    CONFIDENCE = 0.90
    TIMEOUT = 10.0
    _GOOGLE_API_URL = "https://translation.googleapis.com/language/translate/v2"

    def __init__(self):
        self.api_key = settings.GOOGLE_TRANSLATE_API_KEY

    @property
    def is_available(self) -> bool:
        """Returns True only when the API key is present."""
        return bool(self.api_key)

    def is_configured(self) -> bool:
        """Alias method for availability check."""
        return self.is_available

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        Sends translation request to Google Cloud Translation API.

        Raises:
            ProviderError: If key is missing or request fails.
        """
        if not self.is_available:
            raise ProviderError(
                self.SOURCE_USED,
                "GOOGLE_TRANSLATE_API_KEY is not set — skipped silently"
            )

        params = {
            "key": self.api_key,
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(self._GOOGLE_API_URL, params=params)
                response.raise_for_status()
                data = response.json()

                translated = (
                    data.get("data", {})
                    .get("translations", [{}])[0]
                    .get("translatedText")
                )

                if not translated:
                    raise ProviderError(
                        self.SOURCE_USED,
                        "Response did not contain 'translatedText'"
                    )

                return {
                    "translated_text": translated,
                    "source_used": self.SOURCE_USED,
                    "confidence": self.CONFIDENCE,
                }

        except httpx.TimeoutException as e:
            raise ProviderError(self.SOURCE_USED, f"Request timed out: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                self.SOURCE_USED,
                f"HTTP error {e.response.status_code}"
            ) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.SOURCE_USED, f"Unexpected error: {e}") from e

