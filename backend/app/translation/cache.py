"""
backend/app/translation/cache.py
TASK-05: طبقة التخزين المؤقت للترجمة
TRANSLATION_CONTRACT.md:
  - مفتاح: translate:{source}:{target}:{sha256(text)}
  - source_used = 'cache' عند الـ HIT
  - TTL = 3600 ثانية
  - In-Memory افتراضياً + Redis اختياري
  - لا يرفع استثناء عند فشل Redis
"""
import hashlib
import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


def _make_cache_key(source_lang: str, target_lang: str, text: str) -> str:
    """
    يبني مفتاح الكاش وفق صيغة العقد:
    translate:{source_lang}:{target_lang}:{sha256(text)}
    """
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"translate:{source_lang}:{target_lang}:{text_hash}"


class TranslationCache:
    """
    طبقة الكاش المزدوجة:
    - In-Memory Dictionary (افتراضي دائماً).
    - Redis (اختياري — يفعّل عند توفر REDIS_URL).
    لا ترفع أي استثناء خارجياً عند فشل Redis.
    """

    DEFAULT_TTL = 3600  # ثانية

    def __init__(self):
        # In-Memory store: {key: {"value": dict, "expires_at": float}}
        self._memory: dict = {}
        self._redis_client = None
        self._redis_available = False

    async def initialize(self):
        """
        يحاول الاتصال بـ Redis إذا كان REDIS_URL متوفراً.
        فشل Redis لا يوقف التطبيق — يعود للـ In-Memory تلقائياً.
        """
        try:
            from app.core.config import settings
            if settings.REDIS_URL:
                import redis.asyncio as aioredis
                self._redis_client = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                await self._redis_client.ping()
                self._redis_available = True
                logger.info("تم الاتصال بـ Redis بنجاح")
        except Exception:
            # Redis غير متاح — نستمر بالذاكرة المحلية
            self._redis_available = False
            logger.info("Redis غير متاح — تعمل طبقة الكاش بالذاكرة المحلية")

    def _is_memory_expired(self, entry: dict) -> bool:
        """يتحقق إذا كانت القيمة منتهية الصلاحية في In-Memory."""
        return time.monotonic() > entry.get("expires_at", 0)

    async def get(
        self, source_lang: str, target_lang: str, text: str
    ) -> Optional[dict]:
        """
        يبحث عن ترجمة مخزنة.

        Returns:
            dict بـ source_used='cache' عند الـ HIT، أو None عند الـ MISS.
        """
        key = _make_cache_key(source_lang, target_lang, text)

        # محاولة Redis أولاً
        if self._redis_available and self._redis_client:
            try:
                raw = await self._redis_client.get(key)
                if raw:
                    cached_data = json.loads(raw)
                    return {
                        "translated_text": cached_data["translated_text"],
                        "source_used": "cache",
                        "confidence": cached_data.get("confidence"),
                    }
            except Exception:
                # Redis فشل — نرجع للـ In-Memory بصمت
                logger.debug("فشل قراءة Redis — محاولة Fallback للذاكرة المحلية")

        # In-Memory
        entry = self._memory.get(key)
        if entry and not self._is_memory_expired(entry):
            data = entry["value"]
            return {
                "translated_text": data["translated_text"],
                "source_used": "cache",
                "confidence": data.get("confidence"),
            }

        return None  # MISS

    async def set(
        self,
        source_lang: str,
        target_lang: str,
        text: str,
        translated_text: str,
        original_source_used: str,
        confidence: Optional[float] = None,
        ttl: int = DEFAULT_TTL,
    ) -> None:
        """
        يخزن ترجمة جديدة في الكاش.
        لا يرفع أي استثناء عند الفشل.
        """
        key = _make_cache_key(source_lang, target_lang, text)
        value = {
            "translated_text": translated_text,
            "original_source_used": original_source_used,
            "confidence": confidence,
            "cached_at": time.time(),
        }

        # حفظ في Redis
        if self._redis_available and self._redis_client:
            try:
                await self._redis_client.setex(key, ttl, json.dumps(value))
            except Exception:
                logger.debug("فشل الحفظ في Redis — يُحفظ في الذاكرة المحلية بدلاً منه")

        # حفظ دائماً في In-Memory (طبقة احتياط)
        self._memory[key] = {
            "value": value,
            "expires_at": time.monotonic() + ttl,
        }


# مثيل مشترك للتطبيق
translation_cache = TranslationCache()
