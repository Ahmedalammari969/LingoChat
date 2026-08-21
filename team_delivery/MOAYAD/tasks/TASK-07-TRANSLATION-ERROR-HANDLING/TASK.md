# بناء استثناءات وإدارة أخطاء الترجمة

## Task ID
`TASK-07-TRANSLATION-ERROR-HANDLING`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
بناء استثناء TranslationError وتغليف كافة أخطاء المزودين الداخلية وتوفير استجابة آمنة للمستهلكين.

## وصف المهمة
بناء استثناء TranslationError وتغليف كافة أخطاء المزودين الداخلية وتوفير استجابة آمنة للمستهلكين.

## لماذا هذه المهمة مهمة للنظام
عزل أخطاء HTTP والمزودين الخارجيين وحماية خادم الـ WebSocket من الانهيار.

## المتطلبات الوظيفية
- تعريف استثناء TranslationError الموحد.
- التقاط أخطاء المزودين وتغليفها.
- رفع TranslationError فقط عند فشل كافة المحاولات.

## المتطلبات غير الوظيفية
- تجريد تام لأخطاء المزودين.

## Edge Cases / الحالات الحدية
- فشل كل من LibreTranslate و Google و الكاش.

## الملفات المسموح بتعديلها
- `backend/app/translation/service.py`
- `backend/app/translation/errors.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_errors.py`

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
- حالات فشل المزودين.

## المخرجات المطلوبة
- استثناء موحد ومعالجة آمنة.

## نقاط التكامل مع أعضاء الفريق
- يلتقطه الـ WebSocket Router لتسليم النص الأصلي.

## Dependencies
- TASK-06-IDENTITY-TRANSLATION

## شروط اكتمال المهمة
- إدارة أخطاء قوية ومحكمة.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_errors.py -v

## طريقة التسليم
- تقرير فحص إدارة أخطاء الترجمة.

## ممنوعات المهمة
- ممنوع تسريب استثناءات HTTP المباشرة للمستهلكين.
