# بناء مزود الترجمة الأساسي LibreTranslate

## Task ID
`TASK-03-LIBRETRANSLATE-PROVIDER`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
بناء وتطوير فئة LibreTranslateProvider في backend/app/translation/providers.py مع مهلة زمنية 10 ثوانٍ وإرجاع source_used = 'libretranslate'.

## وصف المهمة
بناء وتطوير فئة LibreTranslateProvider في backend/app/translation/providers.py مع مهلة زمنية 10 ثوانٍ وإرجاع source_used = 'libretranslate'.

## لماذا هذه المهمة مهمة للنظام
توفير محرك الترجمة الأساسي مفتوح المصدر للنظام.

## المتطلبات الوظيفية
- إرسال طلب POST لـ LibreTranslate عبر httpx.AsyncClient.
- ضبط timeout=10.0 ثوانٍ.
- إرجاع translated_text و source_used='libretranslate'.
- رفع ProviderError عند الفشل.

## المتطلبات غير الوظيفية
- إدارة الموارد وعدم تسريب الاتصالات.

## Edge Cases / الحالات الحدية
- خادم LibreTranslate غير متاح أو بطيء -> رفع ProviderError لمحاولة الـ Fallback.

## الملفات المسموح بتعديلها
- `backend/app/translation/providers.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_providers.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/TRANSLATION_CONTRACT.md`
- `backend/app/core/config.py`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/database/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `TRANSLATION_CONTRACT.md`
- `SECURITY_CONTRACT.md`

## المدخلات
- نص، لغة المصدر، لغة الهدف.

## المخرجات المطلوبة
- نتيجة الترجمة وقاموس الاستجابة.

## نقاط التكامل مع أعضاء الفريق
- يستدعيه محرك خدمة الترجمة كخيار أول.

## Dependencies
- TASK-02-LANGUAGE-DETECTION

## شروط اكتمال المهمة
- مزود ترجمة أساسي يلتزم بالمهلة والهيكل المعتمد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_providers.py -v

## طريقة التسليم
- تقرير فحص مزود LibreTranslate.

## ممنوعات المهمة
- ممنوع حفظ مفاتيح API في الكود أو تجاوز مهلة 10 ثوانٍ.
