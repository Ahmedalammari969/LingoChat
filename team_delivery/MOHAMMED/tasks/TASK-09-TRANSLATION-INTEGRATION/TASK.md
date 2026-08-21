# دمج معالجة الرسائل مع خدمة الترجمة

## Task ID
`TASK-09-TRANSLATION-INTEGRATION`

## العضو المسؤول
محمد الداعس (Mohammed Al-Daees) - مهندس الويب سوكت

## الهدف
استدعاء دالة translate_message من backend/app/translation/service.py لترجمة الرسائل لكل متلقٍّ بحسب لغته المفضلة.

## وصف المهمة
استدعاء دالة translate_message من backend/app/translation/service.py لترجمة الرسائل لكل متلقٍّ بحسب لغته المفضلة.

## لماذا هذه المهمة مهمة للنظام
تحقيق القيمة الجوهرية لنظام LinguaChat بالترجمة الفورية للرسائل المتداولة.

## المتطلبات الوظيفية
- استدعاء translate_message لكل متلقٍّ في الغرفة بالتوازي.
- تضمين translated_text و translation_source في الرسالة.
- معالجة TranslationError وتسليم النص الأصلي كبديل.

## المتطلبات غير الوظيفية
- عدم تعديل كود الترجمة واستدعاء الواجهة المعتمدة فقط.

## Edge Cases / الحالات الحدية
- فشل الترجمة -> تسليم النص الأصلي مع إشعار خطأ تحذيري.

## الملفات المسموح بتعديلها
- `backend/app/websocket/router.py`

## الملفات المسموح بإنشائها
- `backend/tests/integration/test_websocket_translation.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/TRANSLATION_CONTRACT.md`
- `_TEAM/00_SHARED/WEBSOCKET_CONTRACT.md`

## الملفات الممنوع تعديلها
- `backend/app/translation/** (مملوكة لمؤيد)`
- `frontend/**`
- `backend/app/database/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `TRANSLATION_CONTRACT.md`
- `WEBSOCKET_CONTRACT.md`

## المدخلات
- نص الرسالة ولغات المستقبلين.

## المخرجات المطلوبة
- رسائل مترجمة لكل مستقبل.

## نقاط التكامل مع أعضاء الفريق
- استدعاء خدمة الترجمة التي طورها مؤيد الصوفي.

## Dependencies
- TASK-08-HEARTBEAT-AND-TIMEOUT

## شروط اكتمال المهمة
- ترجمة وتسليم الرسائل المتعددة اللغات بنجاح.

## الاختبارات المطلوبة
- pytest backend/tests/integration/test_websocket_translation.py -v

## طريقة التسليم
- تقرير فحص دمج الترجمة.

## ممنوعات المهمة
- ممنوع تعديل ملفات الترجمة مباشرة.
