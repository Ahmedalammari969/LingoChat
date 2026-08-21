# مزودو خدمة الترجمة: LibreTranslate و Google Fallback (Providers)

## 1. معلومات المهمة

- **رقم المهمة**: `TASK-02-MOAYAD`
- **العضو المسؤول**: مؤيد الصوفي
- **الدور**: مهندس الترجمة والذكاء الاصطناعي
- **الحالة**: جاهزة للتنفيذ بعد TASK-01
- **الأولوية**: حرجة (Critical)

## 2. هدف المهمة

تنفيذ الواجهة المجردة `TranslationProvider` ومزودي الخدمة في `backend/app/translation/providers.py`:
1. `LibreTranslateProvider`: المزود الأساسي (Primary) عبر HTTP API مع مهلة زمنية 10 ثوانٍ.
2. `GoogleTranslateProvider`: المزود الاحتياطي الاختياري (Fallback)، يعمل فقط في حال توفر مفتاح `GOOGLE_TRANSLATE_API_KEY`، ويتخطى بهدوء دون أخطاء في حال عدم ضبطه.

## 3. لماذا هذه المهمة؟

عزل منطق التعامل مع واجهات محركات الترجمة الخارجية (HTTP APIs) وتوفير آلية فشل آمن (Fallback Mechanism) تضمن استمرار عمل التطبيق في حال توقف المزود الأساسي أو بطء استجابته.

## 4. اقرأ هذه الملفات أولاً

- `docs/translation-contract.md` (القسم 6: Provider Interface والقسم 7: Error Handling والقسم 9: Constraints)
- `docs/security.md` (القسم 1: Secrets Management وعدم حفظ المفاتيح في الكود)
- `backend/app/core/config.py` (قراءة `LIBRETRANSLATE_URL`, `LIBRETRANSLATE_API_KEY`, `GOOGLE_TRANSLATE_API_KEY`)

## 5. الملفات المسموح تعديلها

- `backend/app/translation/providers.py`

## 6. الملفات الممنوع تعديلها

- `backend/app/websocket/**` (خاص بمحمد الدعيـس)
- `backend/app/database/**` (خاص بيوسف خيري)
- `frontend/**` (خاص بأحمد العماري)
- `docs/**`

## 7. الملفات التي يمكن إنشاؤها

- `backend/tests/unit/test_translation_providers.py`

## 8. المتطلبات الوظيفية

1. **الواجهة المجردة `TranslationProvider` (ABC/Protocol)**:
   ```python
   class TranslationProvider(ABC):
       @abstractmethod
       async def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
           """
           Returns: {"translated_text": str, "source_used": str, "confidence": float | None}
           Raises: ProviderError on failure.
           """
   ```
2. **المزود الأساسي `LibreTranslateProvider`**:
   - إرسال طلب `POST` غير متزامن عبر `httpx.AsyncClient` إلى `settings.LIBRETRANSLATE_URL/translate`.
   - ضبط `timeout=10.0` ثانية.
   - عند النجاح: إرجاع `{"translated_text": res, "source_used": "libretranslate", "confidence": 0.95}`.
   - عند الفشل (HTTP error, Timeout, Connection error): رفع استثناء `ProviderError("LibreTranslate failed: ...")`.
3. **المزود الاحتياطي `GoogleTranslateProvider` (اختياري)**:
   - فحص وجود `settings.GOOGLE_TRANSLATE_API_KEY`. إذا كان غير موجود، يتم تخطيه أو وسمه بـ `is_available = False`.
   - إذا كان متاحاً: إرسال الطلب، وعند النجاح إرجاع `{"translated_text": res, "source_used": "google", "confidence": 0.90}`.
   - عند الفشل: رفع استثناء `ProviderError`.
4. **استثناءات المزودين**:
   - تعريف `ProviderError(Exception)` داخل `providers.py` أو `core/errors.py`.

## 9. المتطلبات غير الوظيفية

- **الأمان**: عدم طباعة الـ API Keys في الـ Logs نهائياً.
- **إدارة الموارد**: استخدام `httpx.AsyncClient` بشكل آمن لمنع تسريب الاتصالات (Connection Leaks).
- **المهلة الزمنية (Timeout)**: ألا تتجاوز مهلة أي مزود 10 ثوانٍ لمنع تعليق خادم الـ WebSocket.

## 10. Edge Cases (الحالات الطرفية)

- عدم استجابة خادم LibreTranslate (Timeout) -> التقاط الخطأ ورفع `ProviderError` فوراً لمحاولة الـ Fallback.
- إرسال لغة غير مدعومة -> معالجة كود خطأ الـ API ورفع `ProviderError`.
- غياب مفتاح Google API Key -> عدم الانهيار وتخطي المزود بهدوء.
- نص طويل يتجاوز حد المزود -> معالجة الرد الآمن.

## 11. خطوات التنفيذ

- **الخطوة 1**: فحص وتحديث فئات `backend/app/translation/providers.py`.
- **الخطوة 2**: كتابة `LibreTranslateProvider` مع دعم الاتصال غير المتزامن ومهلة 10 ثوانٍ.
- **الخطوة 3**: كتابة `GoogleTranslateProvider` مع دعم التخطي في حال غياب المفتاح.
- **الخطوة 4**: كتابة اختبارات Mock في `backend/tests/unit/test_translation_providers.py` لاختبار سيناريوهات النجاح والفشل والـ Timeout.
- **الخطوة 5**: تشغيل الاختبارات والتأكد من نجاحها.

## 12. Prompt خاص بالمهمة (انسخ هذا النص للذكاء الاصطناعي)

```text
أنت تعمل داخل مشروع LinguaChat الموجود حاليًا.
أنت تنفذ المهمة: TASK-02-MOAYAD (مزودو خدمة الترجمة: LibreTranslate و Google Fallback).

قبل التنفيذ اقرأ الملفات التالية:
- docs/translation-contract.md (الأقسام 6, 7, 9)
- docs/security.md
- backend/app/core/config.py

لا تنشئ مشروعًا جديدًا.
الملفات المسموح لك بتعديلها:
- backend/app/translation/providers.py
- وإنشاء: backend/tests/unit/test_translation_providers.py

إذا وجدت تعارضًا: توقف ولا تخترع حلًا وأبلغ قائد الفريق أحمد.

المطلوب بدقة:
1. تعريف الفئة المجردة TranslationProvider ودالة translate غير المتزامنة.
2. تطبيق LibreTranslateProvider كمزود أساسي (source_used="libretranslate") مع timeout=10s ورفع ProviderError عند الخطأ.
3. تطبيق GoogleTranslateProvider كمزود fallback اختياري (source_used="google") يتخطى تلقائيًا إذا لم يوجد GOOGLE_TRANSLATE_API_KEY.
4. كتابة اختبارات Mock معزولة في backend/tests/unit/test_translation_providers.py تختبر نجاح المزودين، فشل المزود الأساسي، والـ timeout.

نفذ الخطوات وافحص الاختبارات وتأكد من الجودة.
```

## 13. الاختبارات المطلوبة

- اختبار نجاح `LibreTranslateProvider` بإرجاع القاموس بالهيكل المحدد و `source_used="libretranslate"`.
- اختبار فشل `LibreTranslateProvider` ورفع `ProviderError`.
- اختبار سلوك `GoogleTranslateProvider` عند توفر وعدم توفر الـ API Key.
- اختبار مهلة الـ 10 ثوانٍ (Timeout Handling).
- تشغيل: `pytest backend/tests/unit/test_translation_providers.py`

## 14. شروط نجاح المهمة

- التزام كامل بتوقيع وهيكل استجابة `TranslationProvider`.
- عدم انهيار التطبيق عند توقف LibreTranslate.
- نجاح كافة اختبارات المزودين بنسبة 100%.

## 15. شروط عدم النجاح

- كتابة API Keys صريحة في الكود.
- تسريب استثناءات HTTP غير معالجة تسبب انهيار التطبيق.

## 16. ممنوعات قطعية

- ممنوع إضافة مزودي خدمة جدد غير LibreTranslate و Google.
- ممنوع تغيير اسم حقل `source_used` أو `translated_text` أو `confidence`.

## 17. طريقة التسليم

1. انسخ النموذج `_integration/DELIVERY_TEMPLATE.md`.
2. احفظه في مسار: `_integration/Moayad/DELIVERY/DELIVERY-TASK-02.md`.
3. الصق نتائج الاختبارات في التقرير.

## 18. ما الذي يجب أن يخبر به أحمد؟

- إبلاغ أحمد بجهوزية مزودي الترجمة للربط مع طبقة التخزين المؤقت والخدمة الموحدة.
