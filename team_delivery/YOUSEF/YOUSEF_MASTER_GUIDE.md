# دليل المطور التطبيقي الشامل: يوسف خيري (Yousef Khairy)
# مهندس الـ Backend وقواعد البيانات والمصادقة والـ REST (Backend & DB Engineer)

---

## 1. ما هو مشروع LinguaChat وما هي مهمتك بالضبط؟
مشروع **LinguaChat** يعتمد على قاعدة بيانات متينة ونظام مصادقة محكم ومسارات REST سريعة وآمنة.

**مهمتك يا يوسف:**
أنت أساس البيانات والعمود الفقري للأمان في المشروع! مسؤوليتك هي بناء قاعدة بيانات PostgreSQL ونماذج الجداول الخمسة، وهجرات Alembic، وتشفير كلمات المرور وإدارة JWT، وبناء كافة مسارات الـ REST API.

---

## 2. موقعك في المعمارية الهندسية للنظام
```text
+-----------------------------------------------------------------------------------+
|  [نطاقك الحصري - YOUSEF]                                                          |
|  FastAPI Backend & Database Layer                                                 |
|  - 1. REST API Routers: /auth/register, /auth/login, /rooms, /messages, /dashboard|
|  - 2. Security: passlib[bcrypt] cost 12, JWT HS256 (60 min), get_current_user     |
|  - 3. Database: PostgreSQL, SQLAlchemy 2.0 Async, 5 ORM Models, Alembic Migrations |
+-----------------------------------------------------------------------------------+
```

---

## 3. حدود الملكية: ما الذي تعدله وما الممنوع لمسه؟
- ✅ **الملفات المسموح لك بتعديلها**: `backend/app/database/**`, `backend/app/core/security.py`, `backend/app/auth/**`, `backend/app/rooms/**`, `backend/app/messages/**`, `backend/app/dashboard/**`, `backend/alembic/**`, `backend/tests/unit/**`, `team_delivery/YOUSEF/**`.
- ⛔ **الملفات الممنوع لمسها نهائياً**: `frontend/**`, `backend/app/websocket/**`, `backend/app/translation/**`, `docs/**`.

---

## 4. قائمة مهامك الـ 12 بالترتيب:
1. `TASK-01-DATABASE-FOUNDATION`: محرك وجلسات SQLAlchemy غير المتزامنة ودالة `get_db`.
2. `TASK-02-DATABASE-MODELS`: بناء نماذج الجداول الخمسة (`users`, `rooms`, `room_members`, `messages`, `translations`).
3. `TASK-03-DATABASE-MIGRATIONS`: تهيئة وتطبيق هجرات Alembic.
4. `TASK-04-SECURITY-AND-PASSWORD-HASHING`: تشفير Bcrypt cost 12 وصناعة وفك JWT.
5. `TASK-05-AUTH-REGISTRATION-API`: مسار `POST /auth/register` وحفظ المستخدم ولغته.
6. `TASK-06-AUTH-LOGIN-JWT-API`: مسار `POST /auth/login` وإرجاع رمز JWT.
7. `TASK-07-USERS-AUTH-DEPENDENCY`: دالة `get_current_user` لحماية المسارات.
8. `TASK-08-ROOMS-MANAGEMENT-API`: مسارات إنشاء واستعراض الغرف.
9. `TASK-09-ROOM-MEMBERSHIP-API`: مسار الانضمام `POST /rooms/{id}/join` وفحص العضوية.
10. `TASK-10-MESSAGE-PERSISTENCE-AND-HISTORY-API`: مسار استرجاع تاريخ الرسائل المترجمة.
11. `TASK-11-DASHBOARD-STATS-API`: مسار مؤشرات وإحصائيات لوحة التحكم الخمسة.
12. `TASK-12-BACKEND-INTEGRATION-AND-FINAL-QA`: الفحص الشامل وتشغيل كافة اختبارات الـ REST وقاعدة البيانات بنسبة 100%.

---

## 5. خطوات التطبيق العملي خطوة بخطوة:
1. ادخل إلى: `team_delivery/YOUSEF/tasks/TASK-XX/`.
2. اقرأ `TASK.md`.
3. انسخ `01_IMPLEMENT_IDE.md` إلى الذكاء الاصطناعي لتنفيذ الكود المطلوب.
4. شغل الاختبار: `pytest backend/tests/unit/ -v` كما في `02_TEST_IDE.md`.
5. قم بالمراجعة السحابية عبر `03_EXTERNAL_AI_REVIEW.md`.
6. أنشئ تقرير التسليم داخل `handoff/` وانتقل للمهمة التالية.



## 10. المتطلبات الوظيفية وغير الوظيفية والحالات الحدية (FR, NFR & Edge Cases)
- **TASK-02 & 03 (Models & Migrations):**
  - **FR:** نماذج الجداول الخمسة بالـ UUID والمفاتيح الأجنبية، وهجرات Alembic.
  - **NFR:** استعلامات مفهرسة وسريعة (<50ms)، والحذف المتسلسل (CASCADE).
  - **Edge Cases:** تضارب في هجرات Alembic، مفاتيح أجنبية غير مطابقة.
- **TASK-04, 05 & 06 (Security & Auth):**
  - **FR:** تشفير Bcrypt cost 12، توليد JWT HS256 (60 min)، ومسارات التسجيل وتسجيل الدخول.
  - **NFR:** حماية كلمات المرور بنمط تجزئة ثابت زمنياً، حجب `hashed_password` من الاستجابات.
  - **Edge Cases:** اسم مستخدم مكرر (409)، كلمة مرور خاطئة (401 موحد)، توكن منتهي.
- **TASK-08, 09, 10 & 11 (Rooms, Messages, Stats):**
  - **FR:** إنشاء واستعراض الغرف، الانضمام، استرجاع الرسائل المترجمة السابقة، ومقاييس الداشبورد.
  - **NFR:** ترقيم الصفحات (Pagination)، التحقق من العضوية.
  - **Edge Cases:** طلب رسائل غرفة من غير عضو (403)، انضمام متكرر (409)، قاعدة بيانات فارغة.

## 11. دليل حل وتصحيح المشاكل الشائعة فوراً (Troubleshooting Guide)
1. **خطأ `PendingRollbackError`:** استخدام `async with async_session() as session:` مع كتلة `rollback()` عند حدوث خطأ.
2. **خطأ `Target metadata is empty` في Alembic:** استيراد `Base` ونماذج الجداول في `alembic/env.py` وضبط `target_metadata`.
3. **تجنب كشف تفاصيل الأخطاء الحساسة:** الالتزام بنموذج الاستجابة الموحد `{"error": {"code": "...", "message": "..."}}`.
