# دليل المطور: محمد الداعس (MEMBER_README.md)

- **الاسم**: محمد الداعس (Mohammed Al-Daees)
- **الدور**: مهندس الاتصال الفوري والويب سوكت (WebSocket Engineer)
- **نطاق المسؤولية والملكية**:
  - خادم وبروتوكول الـ WebSocket: `backend/app/websocket/**`.
  - اختبارات الويب سوكت: `backend/tests/websocket/**`.
  - مدير الاتصالات `ConnectionManager` ودورة حياة الاتصال والـ Heartbeat.
  - معالجة وتوزيع الرسائل والأحداث الستة (`JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `ERROR`).
  - الربط مع خدمة الترجمة عبر `translate_message` وحفظ الرسائل عبر `messages_service`.
- **الملفات الممنوع تعديلها**:
  - `frontend/**`
  - `backend/app/translation/**` (تستدعي الدالة فقط).
  - `backend/app/database/**` (تستدعي دوال الـ Service فقط).

---

## كيف تبدأ وتنفذ مهامك؟

1. توجه إلى مجلد المهام `_TEAM/MOHAMMED/TASKS/`.
2. اختر المهمة بحسب الترتيب (مثلاً `TASK-01-WEBSOCKET-ANALYSIS`).
3. اقرأ `TASK.md` وتأكد من الملفات المسموحة والممنوعة.
4. انسخ محتوى `01_IMPLEMENT_IDE.md` إلى AI لتنفيذ المهمة.
5. شغل الاختبارات عبر `02_TEST_IDE.md`.
6. قم بالمراجعة السحابية عبر `03_EXTERNAL_AI_REVIEW.md`.
7. عند اجتياز المراجعة بنجاح (`PASS`)، أنشئ تقرير التسليم وأبلغ القائد أحمد.
