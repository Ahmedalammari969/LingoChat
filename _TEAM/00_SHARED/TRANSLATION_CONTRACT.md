# عقد خدمات ومحركات الترجمة (TRANSLATION_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا. يمنع استخدام القيمة `"none"` نهائياً.

---

## 1. الواجهة الرسمية للخدمة (Public Service Interface)

```python
async def translate_message(text: str, source_lang: str, target_lang: str) -> dict:
    """
    Returns:
    {
        "translated_text": str,
        "source_used": "libretranslate" | "google" | "cache" | "identity",
        "confidence": float | None
    }
    Raises:
        TranslationError: When all providers fail.
    """
```

---

## 2. قاعدة الـ Identity الإلزامية
عندما تكون `source_lang == target_lang`:
- إرجاع النص الأصلي فوراً مع `source_used = "identity"` و `confidence = 1.0`.
- يمنع استخدام `"none"` في أي رد أو كود.

---

## 3. عقد كاشف اللغات والتخزين المؤقت
- **كاشف اللغات**: `async def detect_language(text: str) -> str` (إرجاع رمز ISO 639-1 أو `"unknown"` ولا ترفع أي خطأ).
- **مفتاح الكاش**: `translate:{source_lang}:{target_lang}:{sha256(text)}` مع `TTL = 3600s`.
- عند الـ Cache HIT تكون `source_used = "cache"`.
- **المزود الأساسي**: `LibreTranslateProvider` (مهلة 10 ثوانٍ).
- **المزود الاحتياطي**: `GoogleTranslateProvider` (يعمل عند توفر المفتاح).
