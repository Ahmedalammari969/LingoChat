# طبقة التخزين المؤقت للترجمة: In-Memory و Redis Fallback (Cache Layer)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-03-MOAYAD`
- **العضو المسؤول**: مؤيد الصوفي
- **الدور**: مهندس الترجمة والذكاء الاصطناعي
- **الحالة**: جاهزة للتنفيذ بعد TASK-02
- **الأولوية**: عالية (High)

## 2. هدف المهمة

تنفيذ طبقة التخزين المؤقت للترجمة في `backend/app/translation/cache.py` بحيث تعتمد افتراضياً على الذاكرة المحلية (In-Memory Dictionary Cache)، وتدعم Redis اختيارياً عبر `REDIS_URL`، مع التأكد من أن مفتاح الكاش يتبع النمط القياسي المشفر بـ SHA-256، وأن `source_used = "cache"` عند العثور على النتيجة (Cache HIT).

## 3. لماذا هذه المهمة؟

توفير استهلاك موارد الخادم ومزودي الترجمة الخارجيين وتسريع زمن الاستجابة إلى أجزاء من الثانية للنصوص المتكررة (مثل التحيات والعبارات الشائعة).

## 4. اقرأ هذه الملفات أولاً

- `docs/translation-contract.md` (القسم 4 الخاص بـ Cache Contract ونمط المفاتيح والقيم)
- `docs/architecture.md` (القسم 3.5 و 6 - القرار المعماري بأن Redis اختياري)
- `backend/app/core/config.py` (متغير `REDIS_URL`)

## 5. الملفات المسموح تعديلها

- `backend/app/translation/cache.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/database/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_translation_cache.py`

## 8. المتطلبات الوظيفية

1. **صيغة مفتاح الكاش (Cache Key Format)**:
   ```python
   import hashlib

   def generate_cache_key(text: str, source_lang: str, target_lang: str) -> str:
       text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
       return f"translate:{source_lang}:{target_lang}:{text_hash}"
   ```
2. **واجهة الكاش العامة (Cache Functions)**:
   - `get_cached_translation(text: str, source_lang: str, target_lang: str) -> dict | None`:
     - البحث عن المفتاح.
     - في حال العثور على النتيجة (HIT): إرجاع القاموس مع التأكد الحاسم من أن `source_used = "cache"`.
     - في حال عدم العثور (MISS) أو فشل الكاش: إرجاع `None` دون رفع أي خطأ.
   - `set_cached_translation(text: str, source_lang: str, target_lang: str, translation: dict, ttl_seconds: int = 3600) -> None`:
     - حفظ النتيجة في الكاش مع وقت صلاحية TTL (افتراضياً 3600 ثانية).
     - معالجة أي فشل في الحفظ دون رفع استثناء (Fail silently).
3. **التصميم المزدوج (In-Memory Fallback)**:
   - يعمل التطبيق بـ In-Memory Cache افتراضياً.
   - إذا تم توفير `REDIS_URL`، يحاول الاتصال بـ Redis. إذا فشل اتصال Redis أو لم يتوفر، يعود تلقائياً وبسلاسة إلى In-Memory Cache.

## 9. المتطلبات غير الوظيفية

- **عدم الانهيار (Non-fatal Failures)**: فشل الكاش لا يجب أن يوقف عملية الترجمة، بل يتم التحول فوراً لمزودي الخدمة.
- **الأداء**: عمليات القراءة والكتابة في الكاش تتم بشكل غير متزامن فائق السرعة.

## 10. Edge Cases (الحالات الطرفية)

- عدم توفر خادم Redis (Redis Server Down) -> العمل بالذاكرة المحلية دون طباعة أخطاء مزعجة.
- انتهاء مدة صلاحية المفتاح (TTL Expired) -> معاملته كـ Cache MISS وإرجاع `None`.
- نصوص ضخمة أو متعددة الأسطر -> توليد الـ Hash بأمان دون أخطاء في تكوين المفتاح.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث `backend/app/translation/cache.py`.
- **الخطوة 2**: تطبيق خوارزمية توليد المفاتيح عبر SHA-256.
- **الخطوة 3**: بناء فئة الذاكرة المؤقتة `InMemoryCache` ودعم تكامل `RedisCache` الاختياري.
- **الخطوة 4**: تطبيق دوال `get_cached_translation` و `set_cached_translation`.
- **الخطوة 5**: كتابة اختبارات الوحدة في `backend/tests/unit/test_translation_cache.py`.
- **الخطوة 6**: تشغيل الاختبارات والتأكد من نجاحها بالكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-03-MOAYAD (طبقة التخزين المؤقت للترجمة).

قبل التنفيذ اقرأ الملفات التالية:
- docs/translation-contract.md (القسم 4 Cache Contract)
- docs/architecture.md

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/translation/cache.py
- وإنشاء: backend/tests/unit/test_translation_cache.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تطبيق توليد مفتاح الكاش بنمط translate:{source_lang}:{target_lang}:{sha256(text)}.
2. تطبيق get_cached_translation بحيث تعيد القاموس مع source_used="cache" عند الـ HIT، أو None عند الـ MISS.
3. تطبيق set_cached_translation مع دعم TTL=3600.
4. التأكد من أن النظام يعمل افتراضيًا بـ In-Memory Cache مع دعم Redis اختياريًا، وأن فشل الكاش لا يرفع Exception أبدًا.
5. كتابة اختبارات في backend/tests/unit/test_translation_cache.py تختبر التخزين، الاسترجاع، انتهاء الـ TTL، وحالات الـ MISS.

نفذ الخطوات وافحص الاختبارات وتأكد من الجودة.
```

## 13. الاختبارات المطلوبة

- اختبار توليد المفتاح بدقة عبر SHA-256.
- اختبار تخزين واسترجاع ترجمة والتأكد من أن `source_used == "cache"`.
- اختبار حالة الـ Cache Miss والتأكد من إرجاع `None`.
- اختبار عدم تعطل الكود في حال تعذر الاتصال بـ Redis.
- تشغيل: `pytest backend/tests/unit/test_translation_cache.py`

## 14. شروط نجاح المهمة

- تطابق تام لنمط المفاتيح مع العقد.
- إرجاع `source_used = "cache"` دائماً عند الـ HIT.
- عدم انهيار النظام في غياب Redis.
- نجاح كافة اختبارات الكاش بنسبة 100%.

## 15. شروط عدم النجاح

- إرجاع `source_used` بقيمة أخرى غير `"cache"` عند الاسترجاع من الذاكرة المؤقتة.
- توقف النظام أو رمي خطأ عند غياب اتصال Redis.

## 16. ممنوعات قطعية

- ممنوع جعل Redis إلزامياً لتشغيل التطبيق.
- ممنوع تغيير تركيبة مفتاح الكاش المعرفة في العقد.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Moayad/DELIVERY/DELIVERY-TASK-03.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية طبقة الكاش للربط النهائي داخل `service.py`.
