"""
backend/app/translation/detector.py
TASK-02: كاشف اللغات التلقائي
TRANSLATION_CONTRACT.md:
  - يُرجع رمز ISO 639-1 (مثل 'ar', 'en', 'fr').
  - يُرجع 'unknown' عند الفشل / النص الفارغ / الرموز التعبيرية.
  - لا يرفع أي استثناء خارجياً أبداً. NEVER raises an exception.
"""
import logging
import unicodedata

logger = logging.getLogger(__name__)

try:
    from langdetect import detect, LangDetectException
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False
    logger.warning("langdetect غير متوفرة — سيُرجع detect_language دائماً 'unknown'")


def _is_symbolic_only(text: str) -> bool:
    """
    يتحقق إذا كان النص يحتوي على رموز (emojis / symbols) فقط دون أحرف حقيقية.
    """
    for char in text:
        category = unicodedata.category(char)
        # L* = Letters, N* = Numbers
        if category.startswith("L") or category.startswith("N"):
            return False
    return True


async def detect_language(text: str) -> str:
    """
    يكشف لغة النص ويُرجع رمز ISO 639-1.

    Args:
        text: النص الخام المراد كشف لغته.

    Returns:
        رمز ISO 639-1 كـ 'ar', 'en', 'fr', إلخ.
        يُرجع 'unknown' عند:
        - نص فارغ أو يحتوي على مسافات فقط.
        - رموز تعبيرية Emojis فقط.
        - فشل مكتبة langdetect.
        - أي خطأ غير متوقع.
    """
    try:
        # التحقق من النص الفارغ
        if not text or not text.strip():
            return "unknown"

        stripped = text.strip()

        # التحقق من الرموز التعبيرية فقط
        if _is_symbolic_only(stripped):
            return "unknown"

        if not _LANGDETECT_AVAILABLE:
            return "unknown"

        detected = detect(stripped)

        # التأكد من أن المخرج رمز ISO 639-1 صالح (حروف صغيرة، 2-3 أحرف)
        if detected and isinstance(detected, str) and 2 <= len(detected) <= 3:
            return detected.lower()

        return "unknown"

    except Exception:
        # يُحظر رفع أي استثناء خارجياً — TRANSLATION_CONTRACT.md
        logger.debug("فشل كشف اللغة — سيُرجع 'unknown'", exc_info=False)
        return "unknown"
