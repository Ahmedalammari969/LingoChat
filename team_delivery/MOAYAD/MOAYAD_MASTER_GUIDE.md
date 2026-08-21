# دليل المطور التطبيقي الشامل: مؤيد الصوفي (Moayad Al-Soufi)
# مهندس خدمات ومحركات الترجمة والكاش (Translation & Caching Engineer)

---

## 1. ما هو مشروع LinguaChat وما هي مهمتك بالضبط؟
مشروع **LinguaChat** يقوم على الترجمة الفورية الذكية للرسائل بين لغات متعددة دون مقاطعة للمحادثة.

**مهمتك يا مؤيد:**
أنت عقل الترجمة والذكاء الاصطناعي في المشروع! مسؤوليتك هي بناء وحدة الترجمة الشاملة داخل `backend/app/translation/`.

---

## 2. موقعك في المعمارية الهندسية للنظام
```text
+-----------------------------------------------------------------------------------+
|  WebSocket Server (Mohammed) يستدعي خدمتك عبر:                                     |
|  translate_message(text="مرحباً", source_language="ar", target_language="en")     |
+------------------------------------------+----------------------------------------+
                                           | استدعاء مباشر في الذاكرة
                                           v
+-----------------------------------------------------------------------------------+
|  [نطاقك الحصري - MOAYAD]                                                          |
|  Translation Engine Architecture                                                  |
|  - 1. Identity Rule: إذا اللغتان متطابقتان أرجع النص فوراً (source_used="identity") |
|  - 2. Cache Lookup: فحص الكاش بمفتاح SHA-256 (source_used="cache")                 |
|  - 3. LibreTranslate: المزود الأساسي بمهلة 10s (source_used="libretranslate")     |
|  - 4. Google Fallback: المزود الاحتياطي (source_used="google")                    |
+-----------------------------------------------------------------------------------+
```

---

## 3. حدود الملكية: ما الذي تعدله وما الممنوع لمسه؟
- ✅ **الملفات المسموح لك بتعديلها**: `backend/app/translation/**`, `backend/tests/unit/test_translation*`, `team_delivery/MOAYAD/**`.
- ⛔ **الملفات الممنوع لمسها نهائياً**: `frontend/**`, `backend/app/websocket/**`, `backend/app/database/**`, `docs/**`.
- ⚠️ **قاعدة صارمة**: ممنوع استخدام القيمة `"none"` نهائياً في أي حقل.

---

## 4. قائمة مهامك الـ 9 بالترتيب:
1. `TASK-01-TRANSLATION-ANALYSIS`: دراسة عقد الترجمة وقاعدة الـ Identity.
2. `TASK-02-LANGUAGE-DETECTION`: بناء كاشف اللغات `detect_language` مع رموز ISO 639-1.
3. `TASK-03-LIBRETRANSLATE-PROVIDER`: بناء عميل LibreTranslate غير المتزامن بمهلة 10 ثوانٍ.
4. `TASK-04-GOOGLE-FALLBACK-PROVIDER`: بناء المزود الاحتياطي Google Fallback.
5. `TASK-05-TRANSLATION-CACHE`: بناء كاش الترجمة السريع In-Memory و Redis.
6. `TASK-06-IDENTITY-TRANSLATION`: تطبيق قاعدة الـ Identity وتثبيت `confidence = 1.0`.
7. `TASK-07-TRANSLATION-ERROR-HANDLING`: معالجة الاستثناءات وتوليد `TranslationError`.
8. `TASK-08-TRANSLATION-SERVICE-INTEGRATION`: تجميع الوحدات في دالة `translate_message`.
9. `TASK-09-TRANSLATION-FINAL-QA`: الفحص الشامل وتشغيل كافة اختبارات الترجمة والكاش.

---

## 5. خطوات التطبيق العملي خطوة بخطوة:
1. ادخل إلى: `team_delivery/MOAYAD/tasks/TASK-XX/`.
2. اقرأ `TASK.md`.
3. انسخ `01_IMPLEMENT_IDE.md` إلى الذكاء الاصطناعي لكتابة الكود المطلوب.
4. شغل الاختبار: `pytest backend/tests/unit/test_translation* -v` كما في `02_TEST_IDE.md`.
5. قم بالمراجعة السحابية عبر `03_EXTERNAL_AI_REVIEW.md`.
6. أنشئ تقرير التسليم داخل `handoff/` وانتقل للمهمة التالية.



## 10. المتطلبات الوظيفية وغير الوظيفية والحالات الحدية (FR, NFR & Edge Cases)
- **TASK-02 (Language Detection):**
  - **FR:** كشف لغة النص وإرجاع رمز ISO 639-1 قياسي ('ar', 'en', 'fr').
  - **NFR:** زمن استجابة أقل من 5ms وعدم رفع أي كسر.
  - **Edge Cases:** نصوص رموز تعبيرية فقط Emojis (إرجاع 'unknown')، نصوص أرقام فقط.
- **TASK-03 & 04 (Providers & Fallback):**
  - **FR:** استدعاء LibreTranslate أساسياً وتفعيل Google Fallback احتياطياً.
  - **NFR:** مهلة زمنية 10 ثوانٍ (HTTP Timeout 10s).
  - **Edge Cases:** تعطل خادم LibreTranslate، خطأ 500، انقطاع الإنترنت.
- **TASK-05 & 06 (Cache & Identity):**
  - **FR:** تطبيق قاعدة الـ Identity عند تطابق اللغتين، وتخزين الكاش بمفتاح SHA-256.
  - **NFR:** زمن استجابة 0ms للـ Identity، ومدة بقاء للكاش 3600 ثانية.
  - **Edge Cases:** `source_lang == target_lang` (إرجاع `source_used="identity"` وحظر `"none"` نهائياً).

## 11. دليل حل وتصحيح المشاكل الشائعة فوراً (Troubleshooting Guide)
1. **تعليق المحادثة عند بطء خادم LibreTranslate:** ضبط `httpx.AsyncClient(timeout=10.0)` والتقاط `httpx.TimeoutException`.
2. **فشل الاتصال بـ Redis:** استخدام كاش الذاكرة (In-Memory Dict) ككاش احتياطي تلقائي دون كسر التطبيق.
3. **حظر القيمة `"none"`:** التحقق الصارم من حقل `source_used` ليكون من القيم الأربع المصرح بها فقط.
