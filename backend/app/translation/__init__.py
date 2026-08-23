"""
LinguaChat — Translation Module
Implementation: Moayad Al-Soufi
"""
from app.translation.service import translate_message
from app.translation.detector import detect_language
from app.translation.providers import (
    TranslationProvider,
    BaseTranslationProvider,
    LibreTranslateProvider,
    GoogleTranslateProvider,
    ProviderError,
)
from app.translation.cache import (
    TranslationCache,
    translation_cache,
    get_cached_translation,
    set_cached_translation,
)
from app.core.errors import TranslationError

__all__ = [
    "translate_message",
    "detect_language",
    "TranslationProvider",
    "BaseTranslationProvider",
    "LibreTranslateProvider",
    "GoogleTranslateProvider",
    "ProviderError",
    "TranslationCache",
    "translation_cache",
    "get_cached_translation",
    "set_cached_translation",
    "TranslationError",
]
