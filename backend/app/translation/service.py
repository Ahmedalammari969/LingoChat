"""
backend/app/translation/service.py
TASK-06: قاعدة Identity
TASK-07: معالجة الأخطاء وتغليفها
TASK-08: الخدمة الموحدة translate_message

التدفق الكامل وفق TRANSLATION_CONTRACT.md:
Auto Detect → Identity → Cache → LibreTranslate → Google → TranslationError
"""
import logging
from typing import Optional

from app.translation.detector import detect_language
from app.translation.errors import ProviderError, TranslationError
from app.translation.cache import translation_cache
from app.translation.providers import LibreTranslateProvider, GoogleTranslateProvider

logger = logging.getLogger(__name__)

# مثيلات المزودين (مشتركة طوال عمر التطبيق)
_libre_provider = LibreTranslateProvider()
_google_provider = GoogleTranslateProvider()


async def translate_message(
    text: str,
    source_lang: str,
    target_lang: str,
) -> dict:
    """
    الدالة الموحدة الوحيدة التي يستدعيها WebSocket وREST API.

    Args:
        text: النص الخام.
        source_lang: رمز ISO 639-1 للغة المصدر، أو 'auto' للكشف التلقائي.
        target_lang: رمز ISO 639-1 للغة الهدف.

    Returns:
        {
            "translated_text": str,
            "source_used": "libretranslate" | "google" | "cache" | "identity",
            "confidence": float | None
        }

    Raises:
        TranslationError: عند فشل جميع المزودين.
    """

    # ──────────────────────────────────────────────────
    # الخطوة 1: الكشف التلقائي عن اللغة إذا كانت 'auto'
    # ──────────────────────────────────────────────────
    effective_source = source_lang
    if source_lang.strip().lower() == "auto":
        effective_source = await detect_language(text)
        logger.debug("تم كشف اللغة: '%s'", effective_source)

    # ──────────────────────────────────────────────────
    # الخطوة 2: قاعدة Identity الإلزامية (TASK-06)
    # source_lang == target_lang → إرجاع فوري
    # يُحظر تماماً إرجاع source_used = 'none'
    # ──────────────────────────────────────────────────
    if effective_source == target_lang:
        logger.debug("Identity: source == target '%s'", target_lang)
        return {
            "translated_text": text,
            "source_used": "identity",   # ← القيمة الإلزامية الوحيدة هنا
            "confidence": 1.0,
        }

    # ──────────────────────────────────────────────────
    # الخطوة 3: البحث في الكاش
    # ──────────────────────────────────────────────────
    cached = await translation_cache.get(effective_source, target_lang, text)
    if cached is not None:
        logger.debug("Cache HIT: %s→%s", effective_source, target_lang)
        return cached  # source_used = 'cache' مضمون من cache.py

    # ──────────────────────────────────────────────────
    # الخطوة 4: LibreTranslate (المزود الأساسي) — TASK-03
    # ──────────────────────────────────────────────────
    result = await _try_provider(_libre_provider, text, effective_source, target_lang)
    if result:
        await _store_in_cache(effective_source, target_lang, text, result)
        return result

    # ──────────────────────────────────────────────────
    # الخطوة 5: Google Translate (Fallback اختياري) — TASK-04
    # ──────────────────────────────────────────────────
    result = await _try_provider(_google_provider, text, effective_source, target_lang)
    if result:
        await _store_in_cache(effective_source, target_lang, text, result)
        return result

    # ──────────────────────────────────────────────────
    # الخطوة 6: فشل جميع المزودين — TASK-07
    # ──────────────────────────────────────────────────
    logger.error(
        "فشلت جميع محاولات الترجمة: '%s'→'%s'", effective_source, target_lang
    )
    raise TranslationError(
        f"تعذر ترجمة الرسالة من '{effective_source}' إلى '{target_lang}'"
    )


async def _try_provider(
    provider,
    text: str,
    source_lang: str,
    target_lang: str,
) -> Optional[dict]:
    """
    يحاول استدعاء مزود واحد ويعيد None عند الفشل (بدلاً من رفع استثناء).
    يُسجل الخطأ في السجل ويُعيد None لمتابعة الـ Fallback.
    """
    if not provider.is_available:
        return None

    try:
        return await provider.translate(text, source_lang, target_lang)
    except ProviderError as e:
        logger.warning("فشل مزود '%s': %s", e.provider_name, e.reason)
        return None
    except Exception as e:
        logger.error("خطأ غير متوقع في المزود: %s", e)
        return None


async def _store_in_cache(
    source_lang: str,
    target_lang: str,
    text: str,
    result: dict,
) -> None:
    """يخزن نتيجة الترجمة في الكاش بهدوء دون رفع أي استثناء."""
    try:
        await translation_cache.set(
            source_lang=source_lang,
            target_lang=target_lang,
            text=text,
            translated_text=result["translated_text"],
            original_source_used=result["source_used"],
            confidence=result.get("confidence"),
        )
    except Exception:
        # الكاش اختياري — فشله لا يمنع إرجاع النتيجة
        logger.debug("فشل حفظ الترجمة في الكاش", exc_info=False)
