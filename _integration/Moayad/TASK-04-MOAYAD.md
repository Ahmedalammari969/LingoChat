# خدمة الترجمة الموحدة والـ Identity ومعالجة الأخطاء (Unified Service)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-04-MOAYAD`
- **العضو المسؤول**: مؤيد الصوفي
- **الدور**: مهندس الترجمة والذكاء الاصطناعي
- **الحالة**: جاهزة للتنفيذ بعد TASK-01 و TASK-02 و TASK-03
- **الأولوية**: حرجة جداً (Critical - Core Translation Gateway)

## 2. هدف المهمة

تنفيذ الدالة المركزية الموحدة `translate_message` في `backend/app/translation/service.py` التي تدمج دورة تدفق الترجمة الكاملة (كشف اللغات -> الـ Identity -> الكاش -> LibreTranslate -> Google Fallback -> رفع `TranslationError`)، والالتزام الصارم بـ:
`source_used = "identity"` و `confidence = 1.0` عند تطابق لغة المصدر والهدف، ومنع استخدام `"none"` نهائياً.

## 3. لماذا هذه المهمة؟

هذه الخدمة هي نقطة الاتصال الوحيدة والواجهة المجردة (Public Interface) التي يعتمد عليها الـ WebSocket والـ REST API لترجمة كافة الرسائل بين مختلف اللغات دون الحاجة لمعرفة تفاصيل المزودين أو الكاش.

## 4. اقرأ هذه الملفات أولاً

- `docs/translation-contract.md` (الوثيقة الرسمية المجمدة بالكامل، وخاصة الأقسام 1, 2, 5, 7)
- `docs/websocket-contract.md` (حقل `translation_source` وقيم `"libretranslate" | "google" | "cache" | "identity"`)
- `docs/architecture.md` (القسم 5: Data Flow)

## 5. الملفات المسموح تعديلها

- `backend/app/translation/service.py`
- `backend/app/translation/__init__.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/database/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_translation_service.py`
- `backend/tests/integration/test_translation_integration.py`

## 8. المتطلبات الوظيفية

1. **تطبيق دالة `translate_message(text: str, source_lang: str, target_lang: str) -> dict`**:
   - استقبال: `text`, `source_lang`, `target_lang`.
   - **الخطوة أ: معالجة المصدر التلقائي ("auto")**:
     - إذا كانت `source_lang == "auto"`، يتم استدعاء `detect_language(text)`.
     - إذا أعادت `"unknown"`، يتم تعيين `source_lang` افتراضياً أو التعامل معها بحذر.
   - **الخطوة ب: فحص تطابق اللغات (Identity Shortcut)**:
     - إذا كانت `source_lang == target_lang`:
       إرجاع فوري للنتيجة دون استدعاء أي كاش أو مزود خارجي:
       ```python
       return {
           "translated_text": text,
           "source_used": "identity",
           "confidence": 1.0,
       }
       ```
       > **تنبيه صارم**: يمنع منعاً باتاً إرجاع `"none"` أو أي قيمة أخرى غير `"identity"`.
   - **الخطوة ج: فحص الكاش (Cache Lookup)**:
     - استدعاء `get_cached_translation(text, source_lang, target_lang)`.
     - إذا وجد (HIT): إرجاع القاموس المسترجع فوراً (الذي يحتوي `source_used: "cache"`).
   - **الخطوة د: استدعاء المزود الأساسي (LibreTranslate)**:
     - محاولة الترجمة عبر `LibreTranslateProvider`.
     - عند النجاح: حفظ النتيجة في الكاش وإرجاعها للمستدعي.
   - **الخطوة هـ: استدعاء المزود الاحتياطي (Google Fallback)**:
     - في حال فشل المزود الأساسي: محاولة الترجمة عبر `GoogleTranslateProvider` إن كان مهيئاً.
     - عند النجاح: حفظ النتيجة في الكاش وإرجاعها.
   - **الخطوة و: رفع الخطأ الموحد (TranslationError)**:
     - في حال فشل جميع المزودين: رفع استثناء `TranslationError("All translation providers failed.")`.

## 9. المتطلبات غير الوظيفية

- **التجريد التام (Full Abstraction)**: عدم كشف تفاصيل الأخطاء الداخلية للـ Caller، بل تغليفها في `TranslationError`.
- **السرعة**: استجابة فورية لحالات الـ Identity والـ Cache.

## 10. Edge Cases (الحالات الطرفية)

- نص الإدخال `text` فارغ أو مسافات فقط -> معالجة آمنة (إرجاع النص فارغاً مع `"identity"` أو رفع خطأ واضح).
- لغة المصدر والهدف متطابقتان (مثلاً "ar" إلى "ar") -> التأكد 100% أن `source_used == "identity"`.
- انقطاع الإنترنت أو تعطل خادم LibreTranslate مع عدم وجود Google API Key -> رفع `TranslationError` ليتولى الـ WebSocket تسليم النص الأصلي.
- لغة غير مدعومة يطلبها المستخدم -> رفع `TranslationError`.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث `backend/app/translation/service.py`.
- **الخطوة 2**: كتابة دالة `translate_message` بالترتيب المعماري الدقيق (Auto -> Identity -> Cache -> Primary -> Fallback -> Error).
- **الخطوة 3**: التأكد من تصدير `translate_message`, `detect_language`, `TranslationError` في `translation/__init__.py`.
- **الخطوة 4**: كتابة اختبارات الوحدة والتكامل في `backend/tests/unit/test_translation_service.py`.
- **الخطوة 5**: تشغيل كافة اختبارات وحدة الترجمة والتأكد من نجاحها الكامل.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-04-MOAYAD (خدمة الترجمة الموحدة ومعالجة الـ Identity والأخطاء).

قبل التنفيذ اقرأ الملفات التالية:
- docs/translation-contract.md (المصدر النهائي للحقيقة المجمد)
- docs/websocket-contract.md
- docs/architecture.md

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/translation/service.py
- backend/app/translation/__init__.py
- وإنشاء: backend/tests/unit/test_translation_service.py و backend/tests/integration/test_translation_integration.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تطبيق دالة translate_message(text, source_lang, target_lang) غير المتزامنة وفق المخطط الرسمي في docs/translation-contract.md.
2. عند تطابق source_lang == target_lang يجب حتمًا إرجاع:
   {
       "translated_text": text,
       "source_used": "identity",
       "confidence": 1.0
   }
   (يمنع قطعيًا استخدام "none").
3. فحص الكاش واسترجاع النتيجة إذا وجدت، ثم محاولة LibreTranslate ثم Google Fallback.
4. رفع TranslationError إذا فشلت كل المحاولات.
5. كتابة اختبارات شاملة تغطي: Identity, Cache Hit, Primary Success, Fallback Success, Translation Failure.

شغل الاختبارات وتأكد من نجاحها 100%.
```

## 13. الاختبارات المطلوبة

- اختبار حالة الـ Identity: التأكد من تطابق النص ورجوع `source_used == "identity"` و `confidence == 1.0`.
- اختبار حالة الـ Cache Hit: التأكد من رجوع `source_used == "cache"`.
- اختبار المزود الأساسي LibreTranslate والتحقق من `source_used == "libretranslate"`.
- اختبار الـ Fallback عند فشل الأساسي والتحقق من `source_used == "google"`.
- اختبار رفع `TranslationError` عند فشل الجميع.
- تشغيل: `pytest backend/tests/unit/test_translation* -v`

## 14. شروط نجاح المهمة

- تطابق كامل بنسبة 100% مع `docs/translation-contract.md`.
- عدم ظهور القيمة `"none"` في أي رد للترجمة.
- نجاح كافة اختبارات الترجمة (الوحدة والتكامل) بنسبة 100%.

## 15. شروط عدم النجاح

- إرجاع `"none"` في حقل `source_used`.
- عدم معالجة حالة الـ Identity وإرسال طلب غير ضروري لمزودي الترجمة.
- تسريب أخطاء المزودين الداخلية دون تغليفها في `TranslationError`.

## 16. ممنوعات قطعية

- ممنوع استخدام `source_used = "none"` نهائياً.
- ممنوع كسر الواجهة البرمجية الموحدة `translate_message`.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Moayad/DELIVERY/DELIVERY-TASK-04.md`.
3. الصق تقرير نتائج Pytest الكامل للترجمة.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية وحدة الترجمة الشاملة واعتمادها النهائي للربط المباشر مع مهام الـ WebSocket الخاصة بزميلك محمد الدعيـس وتاريخ الرسائل ليوسف خيري.
