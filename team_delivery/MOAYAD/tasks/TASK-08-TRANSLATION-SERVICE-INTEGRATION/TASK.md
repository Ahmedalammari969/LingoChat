# بناء خدمة الترجمة الموحدة الشاملة

## Task ID
`TASK-08-TRANSLATION-SERVICE-INTEGRATION`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
تجميع ودمج دورة تدفق الترجمة الكاملة في دالة translate_message (Auto Detect -> Identity -> Cache -> Primary -> Fallback -> Error).

## وصف المهمة
تجميع ودمج دورة تدفق الترجمة الكاملة في دالة translate_message (Auto Detect -> Identity -> Cache -> Primary -> Fallback -> Error).

## لماذا هذه المهمة مهمة للنظام
توفير الواجهة المركزية الوحيدة التي يعتمد عليها الـ WebSocket والـ REST API لترجمة الرسائل.

## المتطلبات الوظيفية
- تطبيق دالة translate_message بالترتيب المعماري الدقيق.
- تصدير الدوال والاستثناءات في translation/__init__.py.

## المتطلبات غير الوظيفية
- أداء عالٍ واستقرار كامل.

## Edge Cases / الحالات الحدية
- ترجمة نصوص متنوعة ولغات متعددة.

## الملفات المسموح بتعديلها
- `backend/app/translation/service.py`
- `backend/app/translation/__init__.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_service.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/TRANSLATION_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/websocket/**`
- `backend/app/database/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `TRANSLATION_CONTRACT.md`

## المدخلات
- طلبات ترجمة الرسائل.

## المخرجات المطلوبة
- نتائج الترجمة الموحدة.

## نقاط التكامل مع أعضاء الفريق
- يستدعيها محمد الداعس في الـ WebSocket ويوسف خيري في تاريخ الرسائل.

## Dependencies
- TASK-07-TRANSLATION-ERROR-HANDLING

## شروط اكتمال المهمة
- خدمة ترجمة موحدة متكاملة ومطابقة 100% للعقد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_service.py -v

## طريقة التسليم
- تقرير فحص خدمة الترجمة الموحدة.

## ممنوعات المهمة
- ممنوع تغيير توقيع دالة translate_message.
