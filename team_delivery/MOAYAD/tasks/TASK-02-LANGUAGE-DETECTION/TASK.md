# بناء وحدة كشف اللغات التلقائي

## Task ID
`TASK-02-LANGUAGE-DETECTION`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
بناء وتطوير دالة async def detect_language(text: str) -> str في backend/app/translation/detector.py لإرجاع رمز ISO 639-1 أو 'unknown' دون رفع أي استثناء.

## وصف المهمة
بناء وتطوير دالة async def detect_language(text: str) -> str في backend/app/translation/detector.py لإرجاع رمز ISO 639-1 أو 'unknown' دون رفع أي استثناء.

## لماذا هذه المهمة مهمة للنظام
التعرف على لغة الرسائل غير المحددة وتوجيهها للمترجم الصحيح.

## المتطلبات الوظيفية
- كشف اللغة وإرجاع رمز ISO 639-1 (مثل ar, en, fr).
- إرجاع 'unknown' عند الفشل أو الرموز دون رفع Exception.

## المتطلبات غير الوظيفية
- سرعة تنفيذ فائقة (أقل من 20ms) وعدم الانهيار.

## Edge Cases / الحالات الحدية
- رموز تعبيرية Emojis فقط -> 'unknown'.
- نص فارغ -> 'unknown'.
- نصوص مختلطة.

## الملفات المسموح بتعديلها
- `backend/app/translation/detector.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_detector.py`

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
- النص الخام.

## المخرجات المطلوبة
- رمز اللغة ISO 639-1 أو 'unknown'.

## نقاط التكامل مع أعضاء الفريق
- تستدعيها خدمة الترجمة عند تمرير لغة المصدر 'auto'.

## Dependencies
- TASK-01-TRANSLATION-ANALYSIS

## شروط اكتمال المهمة
- كاشف لغات مستقر لا يرفع أي استثناء.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_detector.py -v

## طريقة التسليم
- تقرير فحص كاشف اللغات.

## ممنوعات المهمة
- ممنوع رفع أي استثناء خارج الدالة detect_language.
