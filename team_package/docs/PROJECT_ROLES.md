# مصفوفة الأدوار والمسؤوليات وحدود الملكية (PROJECT_ROLES.md)

تحدد هذه الوثيقة الأدوار الأربعة لأعضاء فريق **LinguaChat**، وحدود الملكية الصارمة للملفات، وما هو مسموح وممنوع لكل عضو.

---

## 1. أحمد العماري (Ahmed Alammari)
- **المسمى**: قائد المشروع (Project Leader) + مهندس الواجهات الأمامية (Frontend Engineer) + مسؤول الدمج وضمان الجودة (Integration & Final QA).
- **المسؤوليات**:
  - قيادة الفريق والتنسيق العام واعتماد تقارير التسليم.
  - بناء وتطوير واجهات المستخدم (React SPA) وتجربة المستخدم (UI/UX).
  - تطوير عميل الـ API المركزي وعميل WebSocket في الـ Frontend.
  - إدارة الجلسات وتخزين JWT في `localStorage`.
  - إجراء الفحص الشامل وتدقيق العقود والدمج النهائي واختبارات الـ Regression.
- **الملفات المسموح بتعديلها (Allowed Files)**:
  - `frontend/src/**` (الصفحات، المكونات، الخطافات، التنسيقات، الخدمات).
  - `_integration/**` (ملفات المتابعة والتقارير والدمج).
- **الملفات الممنوع تعديلها (Forbidden Files)**:
  - `backend/app/database/**`
  - `backend/app/auth/**`
  - `backend/app/rooms/**`
  - `backend/app/messages/**`
  - `backend/app/websocket/**`
  - `backend/app/translation/**`

---

## 2. محمد الداعس (Mohammed Al-Daees)
- **المسمى**: مهندس الاتصال الفوري والويب سوكت (WebSocket Engineer).
- **المسؤوليات**:
  - بناء وتطوير نقطة اتصال الويب سوكت `/ws/{room_id}`.
  - تطوير مدير الاتصالات `ConnectionManager` وتتبع الاتصالات الحية.
  - التحقق الأمني اللحظي من توكن JWT وعضوية الغرفة وإغلاق الاتصال بالأكواد المعتمدة (`4001`, `4003`, `4004`).
  - معالجة أحداث الويب سوكت الستة: `JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `ERROR`.
  - دمج الرسائل مع خدمة الترجمة لحساب الترجمة لكل مستقبل وتخزين الرسائل في قاعدة البيانات.
  - كتابة اختبارات الويب سوكت الشاملة.
- **الملفات المسموح بتعديلها (Allowed Files)**:
  - `backend/app/websocket/**` (`router.py`, `manager.py`, `schemas.py`, `protocol.py`).
  - `backend/tests/websocket/**`.
- **الملفات الممنوع تعديلها (Forbidden Files)**:
  - `frontend/**`
  - `backend/app/translation/**` (يستدعي واجهة `translate_message` فقط).
  - `backend/app/database/**` و `backend/app/database/models/**` (يستدعي دوال الـ Service فقط).
  - `backend/app/auth/router.py`

---

## 3. مؤيد الصوفي (Moayad Al-Soufi)
- **المسمى**: مهندس خدمات ومحركات الترجمة (Translation Engineer).
- **المسؤوليات**:
  - تطوير وحدة كشف اللغات التلقائي `detect_language` وفق معايير ISO 639-1.
  - تطوير مزود الترجمة الأساسي `LibreTranslateProvider` والمزود الاحتياطي `GoogleTranslateProvider`.
  - تطوير طبقة التخزين المؤقت للترجمة `TranslationCache` (In-Memory + Redis Fallback).
  - تطبيق خدمة الترجمة الموحدة `translate_message` مع الالتزام التام بقاعدة `source_used = "identity"`.
  - إدارة أخطاء الترجمة وتوفير الواجهة المجردة لكافة المستهلكين.
  - كتابة اختبارات الترجمة الشاملة.
- **الملفات المسموح بتعديلها (Allowed Files)**:
  - `backend/app/translation/**` (`detector.py`, `providers.py`, `cache.py`, `service.py`, `__init__.py`).
  - `backend/tests/translation/**` أو `backend/tests/unit/test_translation*`.
- **الملفات الممنوع تعديلها (Forbidden Files)**:
  - `frontend/**`
  - `backend/app/websocket/**`
  - `backend/app/database/**`
  - `backend/app/auth/**`

---

## 4. يوسف خيري (Yousef Khairy)
- **المسمى**: مهندس قواعد البيانات والـ Backend REST API والمصادقة (Backend / Database / REST Engineer).
- **المسؤوليات**:
  - إعداد اتصال ومحرك قاعدة البيانات غير المتزامن وجداول PostgreSQL وهجرات Alembic.
  - بناء نماذج SQLAlchemy لـ `users`, `rooms`, `room_members`, `messages`, `translations`.
  - تطبيق دوال التشفير والأمان وإصدار وفك رموز JWT.
  - تطبيق مسارات المصادقة `/auth/register` و `/auth/login` ودالة `get_current_user`.
  - تطبيق مسارات الغرف `/rooms` والانضمام والتحقق من العضوية.
  - تطبيق مسارات حفظ واسترجاع الرسائل السابقة المترجمة `/rooms/{room_id}/messages`.
  - تطبيق مسار لوحة التحكم والإحصائيات `/dashboard/stats`.
  - كتابة اختبارات الوحدة والتكامل للـ REST API.
- **الملفات المسموح بتعديلها (Allowed Files)**:
  - `backend/app/database/**`
  - `backend/app/auth/**`
  - `backend/app/users/**`
  - `backend/app/rooms/**`
  - `backend/app/messages/**`
  - `backend/app/dashboard/**`
  - `backend/tests/unit/test_auth*`, `test_rooms*`, `test_messages*`, `test_dashboard*`, `test_database*`, `test_security*`.
- **الملفات الممنوع تعديلها (Forbidden Files)**:
  - `frontend/**`
  - `backend/app/websocket/**`
  - `backend/app/translation/**`

---

## 5. مصفوفة الصلاحيات المشتركة (Cross-Component Matrix)

```text
┌─────────────────┬──────────┬───────────┬───────────┬──────────┐
│ Module / Path   │ Ahmed    │ Mohammed  │ Moayad    │ Yousef   │
├─────────────────┼──────────┼───────────┼───────────┼──────────┤
│ frontend/       │ OWN (W)  │ FORBIDDEN │ FORBIDDEN │ FORBIDDEN│
│ websocket/      │ READ     │ OWN (W)   │ FORBIDDEN │ FORBIDDEN│
│ translation/    │ READ     │ CALL ONLY │ OWN (W)   │ FORBIDDEN│
│ database/auth/  │ READ     │ CALL ONLY │ FORBIDDEN │ OWN (W)  │
│ team_package/   │ READ     │ READ ONLY │ READ ONLY │ READ ONLY│
│ _integration/   │ LEAD (W) │ HANDOFF(W)│ HANDOFF(W)│ HANDOFF(W│
└─────────────────┴──────────┴───────────┴───────────┴──────────┘
```
*(W = Write / Modify Permission)*
