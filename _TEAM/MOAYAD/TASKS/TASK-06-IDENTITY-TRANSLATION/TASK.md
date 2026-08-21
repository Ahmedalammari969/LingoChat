# تطبيق قاعدة الـ Identity لتطابق اللغات

## Task ID
`TASK-06-IDENTITY-TRANSLATION`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
تطبيق القاعدة الصارمة: عندما تكون source_lang == target_lang يجب إعادة النص الأصلي فوراً مع source_used = 'identity' و confidence = 1.0 مع منع استخدام 'none'.

## وصف المهمة
تطبيق القاعدة الصارمة: عندما تكون source_lang == target_lang يجب إعادة النص الأصلي فوراً مع source_used = 'identity' و confidence = 1.0 مع منع استخدام 'none'.

## لماذا هذه المهمة مهمة للنظام
تجنب إرسال طلبات ترجمة غير ضرورية للنصوص التي لا تحتاج ترجمة.

## المتطلبات الوظيفية
- فحص تطابق اللغات وإرجاع النص الأصلي فوراً.
- تعيين source_used = 'identity' و confidence = 1.0.
- حظر تام لاستخدام القيمة 'none'.

## المتطلبات غير الوظيفية
- استجابة فورية بدون أي تأخير.

## Edge Cases / الحالات الحدية
- طلب ترجمة عربي إلى عربي 'ar' -> 'ar'.

## الملفات المسموح بتعديلها
- `backend/app/translation/service.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_identity.py`

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
- نصوص ذات لغات متطابقة.

## المخرجات المطلوبة
- نتيجة الـ Identity الفورية.

## نقاط التكامل مع أعضاء الفريق
- خطوة الاختصار الأولى داخل خدمة translate_message.

## Dependencies
- TASK-05-TRANSLATION-CACHE

## شروط اكتمال المهمة
- تطبيق قاعدة الـ Identity بدقة متناهية.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_identity.py -v

## طريقة التسليم
- تقرير فحص قاعدة الـ Identity.

## ممنوعات المهمة
- ممنوع استخدام القيمة 'none' مطلقاً.
