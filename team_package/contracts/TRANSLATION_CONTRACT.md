# عقد خدمات ومحركات وكاش الترجمة (TRANSLATION_CONTRACT.md)
# FROZEN CONTRACT - DO NOT MODIFY

> **الحالة**: مجمد رسميًا (Frozen Contract).  
> يمنع استخدام القيمة `"none"`. القيم المعتمدة حصراً لـ `source_used` هي: `"libretranslate"`, `"google"`, `"cache"`, `"identity"`.

---

## 1. الواجهة البرمجية الموحدة للخدمة (Public Service Interface)

المستهلكون (مثل WebSocket Router و REST History) يستدعون هذه الدالة حصراً دون معرفة تفاصيل المزودين أو الكاش:

```python
async def translate_message(
    text: str,
    source_lang: str,
    target_lang: str
) -> dict:
    """
    Translates a message from source_lang to target_lang.
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

## 2. قاعدة الـ Identity الإلزامية (The Identity Shortcut)

عندما تكون لغة المصدر مطابقة للغة الهدف (`source_lang == target_lang`):
- يعاد النص الأصلي فوراً دون استدعاء أي كاش أو مزود خارجي:
```json
{
  "translated_text": "<original_text>",
  "source_used": "identity",
  "confidence": 1.0
}
```
> **تنبيه صارم**: يمنع منعاً باتاً إرجاع `"none"` أو أي قيمة أخرى غير `"identity"`.

---

## 3. عقد كاشف اللغات التلقائي (`detect_language`)

```python
async def detect_language(text: str) -> str:
    """
    Detects language and returns ISO 639-1 code (e.g. 'ar', 'en', 'fr').
    Returns 'unknown' on failure or empty/symbolic input.
    NEVER raises an exception.
    """
```

---

## 4. عقد التخزين المؤقت (Cache Contract)

- **صيغة مفتاح الكاش**: `translate:{source_lang}:{target_lang}:{sha256(text)}`
- **القيمة المخزنة**: JSON String يحتوي النص المترجم والمزود الأصلي وتاريخ التخزين.
- **مدة الصلاحية الافتراضية (TTL)**: 3600 ثانية (ساعة واحدة).
- **عند العثور على النتيجة (Cache HIT)**: يجب أن تكون `source_used = "cache"`.
- **التصميم المزدوج**: In-Memory Dictionary افتراضياً، مع دعم اختياري لـ Redis Fallback عند توفر `REDIS_URL`.

---

## 5. مزودو الترجمة وآلية الفشل الآمن (Providers & Fallback)

1. **المزود الأساسي (`LibreTranslateProvider`)**:
   - إرسال طلب POST إلى `LIBRETRANSLATE_URL/translate` بمهلة زمنية **10 ثوانٍ**.
   - عند النجاح: `source_used = "libretranslate"`, `confidence = 0.95`.
2. **المزود الاحتياطي الاختياري (`GoogleTranslateProvider`)**:
   - يعمل فقط في حال توفر مفتاح `GOOGLE_TRANSLATE_API_KEY`.
   - عند النجاح: `source_used = "google"`, `confidence = 0.90`.
3. **في حال فشل جميع المزودين**:
   - رفع استثناء `TranslationError` الموحد ليقوم الـ WebSocket بتسليم النص الأصلي للمستخدم مع إرسال إشعار `ERROR`.
