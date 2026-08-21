# دليل المطور: مؤيد الصوفي (MEMBER_README.md)

- **الاسم**: مؤيد الصوفي (Moayad Al-Soufi)
- **الدور**: مهندس خدمات ومحركات الترجمة والكاش (Translation Engineer)
- **نطاق المسؤولية والملكية**:
  - وحدة كشف اللغات: `backend/app/translation/detector.py`.
  - مزودو الترجمة: `backend/app/translation/providers.py` (`LibreTranslateProvider`, `GoogleTranslateProvider`).
  - طبقة الكاش: `backend/app/translation/cache.py` (In-Memory + Redis Fallback).
  - خدمة الترجمة الموحدة: `backend/app/translation/service.py`.
  - اختبارات الترجمة: `backend/tests/translation/**` أو `backend/tests/unit/test_translation*`.
- **الملفات الممنوع تعديلها**:
  - `frontend/**`
  - `backend/app/websocket/**`
  - `backend/app/database/**`

---

## كيف تبدأ وتنفذ مهامك؟

1. توجه إلى مجلد المهام `_TEAM/MOAYAD/TASKS/`.
2. اختر المهمة بحسب الترتيب (مثلاً `TASK-01-TRANSLATION-ANALYSIS`).
3. اقرأ `TASK.md` وتأكد من شروط العقد.
4. انسخ محتوى `01_IMPLEMENT_IDE.md` إلى AI لتنفيذ المهمة.
5. شغل الاختبارات عبر `02_TEST_IDE.md`.
6. قم بالمراجعة السحابية عبر `03_EXTERNAL_AI_REVIEW.md`.
7. عند اجتياز المراجعة بنجاح (`PASS`)، أنشئ تقرير التسليم وأبلغ القائد أحمد.
