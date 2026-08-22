"""
backend/app/translation/providers.py
TASK-03: LibreTranslateProvider
TASK-04: GoogleTranslateProvider (احتياطي اختياري)
TRANSLATION_CONTRACT.md & SECURITY_CONTRACT.md
"""
import logging
from abc import ABC, abstractmethod

import httpx

from app.core.config import settings
from app.translation.errors import ProviderError

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# الواجهة المجردة للمزودين
# ─────────────────────────────────────────────

class BaseTranslationProvider(ABC):
    """واجهة مجردة يجب أن يرثها كل مزود ترجمة."""

    @abstractmethod
    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        يُترجم النص ويُرجع dict بالشكل المعتمد في TRANSLATION_CONTRACT:
        {
            "translated_text": str,
            "source_used": "libretranslate" | "google",
            "confidence": float
        }
        يرفع ProviderError عند الفشل.
        """
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """يُرجع True إذا كان المزود متاحاً (تكوينه مكتمل)."""
        ...


# ─────────────────────────────────────────────
# TASK-03: LibreTranslate (المزود الأساسي)
# ─────────────────────────────────────────────

class LibreTranslateProvider(BaseTranslationProvider):
    """
    المزود الأساسي لخدمة الترجمة.
    يُرسل POST إلى LIBRETRANSLATE_URL/translate بـ httpx.AsyncClient.
    timeout=10.0 ثانية وفق TRANSLATION_CONTRACT.
    """

    SOURCE_USED = "libretranslate"
    CONFIDENCE = 0.95
    TIMEOUT = 10.0

    @property
    def is_available(self) -> bool:
        return bool(settings.LIBRETRANSLATE_URL)

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        يُرسل طلب ترجمة لـ LibreTranslate.

        Raises:
            ProviderError: عند فشل الطلب أو خطأ HTTP أو انتهاء الوقت.
        """
        if not self.is_available:
            raise ProviderError(self.SOURCE_USED, "LIBRETRANSLATE_URL غير مُهيأ")

        url = f"{settings.LIBRETRANSLATE_URL.rstrip('/')}/translate"
        payload = {
            "q": text,
            "source": source_lang,
            "target": target_lang,
            "format": "text",
        }

        # إضافة مفتاح API إذا كان متوفراً
        if settings.LIBRETRANSLATE_API_KEY:
            payload["api_key"] = settings.LIBRETRANSLATE_API_KEY

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

                translated = data.get("translatedText")
                if not translated:
                    raise ProviderError(
                        self.SOURCE_USED,
                        "الاستجابة لا تحتوي على translatedText"
                    )

                return {
                    "translated_text": translated,
                    "source_used": self.SOURCE_USED,
                    "confidence": self.CONFIDENCE,
                }

        except httpx.TimeoutException as e:
            raise ProviderError(self.SOURCE_USED, f"انتهى وقت الانتظار: {e}") from e
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                self.SOURCE_USED,
                f"خطأ HTTP {e.response.status_code}"
            ) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.SOURCE_USED, f"خطأ غير متوقع: {e}") from e


# ─────────────────────────────────────────────
# TASK-04: Google Translate (المزود الاحتياطي الاختياري)
# ─────────────────────────────────────────────

class GoogleTranslateProvider(BaseTranslationProvider):
    """
    المزود الاحتياطي الاختياري.
    يعمل فقط عند توفر GOOGLE_TRANSLATE_API_KEY.
    يُتخطى بهدوء تام إذا لم يكن المفتاح موجوداً.
    يُحظر طباعة المفتاح في السجلات — SECURITY_CONTRACT.
    """

    SOURCE_USED = "google"
    CONFIDENCE = 0.90
    TIMEOUT = 10.0
    _GOOGLE_API_URL = "https://translation.googleapis.com/language/translate/v2"

    @property
    def is_available(self) -> bool:
        """يُرجع True فقط عند وجود المفتاح."""
        return bool(settings.GOOGLE_TRANSLATE_API_KEY)

    async def translate(
        self, text: str, source_lang: str, target_lang: str
    ) -> dict:
        """
        يُرسل طلب ترجمة لـ Google Translate API v2.

        Raises:
            ProviderError: إذا لم يكن المفتاح متوفراً أو فشل الطلب.
        """
        if not self.is_available:
            # تخطي بهدوء — لا تطبع المفتاح أبداً
            raise ProviderError(
                self.SOURCE_USED,
                "GOOGLE_TRANSLATE_API_KEY غير موجود — يُتخطى تلقائياً"
            )

        params = {
            "key": settings.GOOGLE_TRANSLATE_API_KEY,
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
                        "الاستجابة لا تحتوي على translatedText"
                    )

                return {
                    "translated_text": translated,
                    "source_used": self.SOURCE_USED,
                    "confidence": self.CONFIDENCE,
                }

        except httpx.TimeoutException as e:
            raise ProviderError(self.SOURCE_USED, f"انتهى وقت الانتظار: {e}") from e
        except httpx.HTTPStatusError as e:
            # يُحظر تسجيل المفتاح في السجلات
            raise ProviderError(
                self.SOURCE_USED,
                f"خطأ HTTP {e.response.status_code}"
            ) from e
        except ProviderError:
            raise
        except Exception as e:
            raise ProviderError(self.SOURCE_USED, f"خطأ غير متوقع: {e}") from e
