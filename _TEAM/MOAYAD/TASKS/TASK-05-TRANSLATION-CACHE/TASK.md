# بناء طبقة التخزين المؤقت للترجمة

## Task ID
`TASK-05-TRANSLATION-CACHE`

## العضو المسؤول
مؤيد الصوفي (Moayad Al-Soufi) - مهندس الترجمة

## الهدف
بناء وتطوير كاش الترجمة في backend/app/translation/cache.py بنمط In-Memory Dictionary افتراضياً مع دعم Redis Fallback، ومفتاح SHA-256 و source_used = 'cache'.

## وصف المهمة
بناء وتطوير كاش الترجمة في backend/app/translation/cache.py بنمط In-Memory Dictionary افتراضياً مع دعم Redis Fallback، ومفتاح SHA-256 و source_used = 'cache'.

## لماذا هذه المهمة مهمة للنظام
تسريع زمن استجابة الترجمة للنصوص المتكررة وتوفير استهلاك موارد الخوادم.

## المتطلبات الوظيفية
- توليد المفتاح translate:{source}:{target}:{sha256(text)}.
- دالة get_cached_translation وإرجاع source_used='cache' عند الـ HIT.
- دالة set_cached_translation مع TTL=3600.
- عدم رفع استثناء عند فشل الكاش.

## المتطلبات غير الوظيفية
- سرعة قراءة وكتابة فائقة.

## Edge Cases / الحالات الحدية
- عدم توفر خادم Redis -> العمل بالذاكرة المحلية دون أخطاء.

## الملفات المسموح بتعديلها
- `backend/app/translation/cache.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_translation_cache.py`

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
- نص ومفاتيح اللغات.

## المخرجات المطلوبة
- استرجاع وحفظ الترجمات في الكاش.

## نقاط التكامل مع أعضاء الفريق
- تستدعيها خدمة الترجمة قبل استدعاء المزودين الخارجيين.

## Dependencies
- TASK-04-GOOGLE-FALLBACK-PROVIDER

## شروط اكتمال المهمة
- كاش ترجمة متوافق 100% مع العقد.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_translation_cache.py -v

## طريقة التسليم
- تقرير فحص كاش الترجمة.

## ممنوعات المهمة
- ممنوع إرجاع أي قيمة غير 'cache' في source_used عند الاسترجاع من الكاش.
