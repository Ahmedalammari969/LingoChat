# بناء مزود الترجمة الاحتياطي Google Fallback

## Task ID
`TASK-04-GOOGLE-FALLBACK-PROVIDER`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
بناء وتطوير فئة GoogleTranslateProvider كمزود احتياطي اختياري يعمل عند توفر GOOGLE_TRANSLATE_API_KEY مع source_used = 'google'.

## وصف المهمة
بناء وتطوير فئة GoogleTranslateProvider كمزود احتياطي اختياري يعمل عند توفر GOOGLE_TRANSLATE_API_KEY مع source_used = 'google'.

## لماذا هذه المهمة مهمة للنظام
ضمان استمرارية الترجمة في حال توقف أو بطء المزود الأساسي.

## المتطلبات الوظيفية
- فحص وجود المفتاح وتخطي المزود بهدوء إذا لم يتوفر.
- إرسال طلب الترجمة عند التوفر وإرجاع source_used='google'.
- رفع ProviderError عند الفشل.

## المتطلبات غير الوظيفية
- أمان المفاتيح وعدم طباعتها في السجلات.

## Edge Cases / الحالات الحدية
- غياب المفتاح -> تخطي فوري دون أخطاء.

## الملفات المسموح بتعديلها
- `backend/app/translation/providers.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_fallback.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/TRANSLATION_CONTRACT.md`
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`

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
- نتيجة الترجمة الاحتياطية.

## نقاط التكامل مع أعضاء الفريق
- يستدعيه محرك الترجمة عند فشل LibreTranslate.

## Dependencies
- TASK-03-LIBRETRANSLATE-PROVIDER

## شروط اكتمال المهمة
- مزود احتياطي مرن وآمن.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_fallback.py -v

## طريقة التسليم
- تقرير فحص المزود الاحتياطي.

## ممنوعات المهمة
- ممنوع جعل المزود الاحتياطي إلزامياً لتشغيل النظام.
