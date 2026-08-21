# دليل مهام المطور: يوسف خيري (Yousef Khairy)
# Backend, Database & REST API Engineering Guide

> **الدور الأساسي**: مهندس قواعد البيانات والمصادقة وخدمات REST API  
> **المسؤولية البرمجية**: Database Models + Migrations + Auth + Users + Rooms + Messages Persistence + Dashboard Stats + REST Endpoints  
> **المستندات المرجعية الأساسية**: `docs/database-schema.md` ، `docs/api-contract.md` ، `docs/security.md` ، `docs/architecture.md`

---

## 1. نطاق المسؤولية والملكية (Ownership)

### ما تملكه وتتحكم به بالكامل (Allowed Scope):
- نماذج قاعدة البيانات (SQLAlchemy Async Models): `users`, `rooms`, `room_members`, `messages`, `translations`.
- جلسات واتصال قاعدة البيانات: `backend/app/database/session.py`, `base.py`.
- خدمات التحقق والتشفير وإنشاء توكن JWT: `backend/app/core/security.py`, `backend/app/auth/**`.
- منطق الغرف والتحقق من العضوية: `backend/app/rooms/**`.
- استرجاع وتخزين الرسائل: `backend/app/messages/**`.
- إحصائيات لوحة التحكم: `backend/app/dashboard/**`.
- اختبارات الـ Unit والـ Integration الخاصة بهذه الوحدات: `backend/tests/unit/**`, `backend/tests/integration/**`.

### ما لا تملكه ويمنع التعديل عليه (Forbidden Scope):
- **خدمة WebSocket**: مملوكة بالكامل لزميلك **محمد الدعيـس** (`backend/app/websocket/**`).
- **محركات وكاش الترجمة**: مملوكة بالكامل لزميلك **مؤيد الصوفي** (`backend/app/translation/**`).
- **واجهة المستخدم Frontend**: مملوكة بالكامل للقائد **أحمد العماري** (`frontend/**`).

---

## 2. خريطة تسلسل المهام (Task Sequence)

| رقم المهمة | اسم المهمة | الملفات الأساسية | الأولوية |
| :--- | :--- | :--- | :--- |
| **TASK-01-YOUSEF** | إعداد قاعدة البيانات ونماذج الجداول الأساسية (SQLAlchemy Models & Session) | `database/session.py`, `database/base.py`, `database/models/*` | حرجة (عاجل) |
| **TASK-02-YOUSEF** | نموذج المستخدم وخدمات التشفير والتحقق (User Model & Security Utilities) | `core/security.py`, `database/models/user.py`, `users/*` | حرجة |
| **TASK-03-YOUSEF** | وحدة المصادقة والتسجيل وإصدار JWT (Auth Service, Schemas & Router) | `auth/schemas.py`, `auth/service.py`, `auth/router.py` | حرجة |
| **TASK-04-YOUSEF** | إدارة الغرف والانضمام والتحقق من العضوية (Rooms Module) | `rooms/schemas.py`, `rooms/service.py`, `rooms/router.py` | عالية |
| **TASK-05-YOUSEF** | حفظ الرسائل واسترجاع تاريخ المحادثات (Messages Persistence & History) | `messages/schemas.py`, `messages/service.py`, `rooms/router.py` | عالية |
| **TASK-06-YOUSEF** | إحصائيات لوحة التحكم ومؤشرات النظام (Dashboard Stats API) | `dashboard/service.py`, `dashboard/router.py` | متوسطة |
| **TASK-07-YOUSEF** | حزمة الاختبارات الشاملة للـ Backend (Unit & Integration Test Suite) | `backend/tests/unit/*`, `backend/tests/integration/*` | عالية |

---

## 3. إرشادات العمل اليومي واستخدام الذكاء الاصطناعي (AI Workflow)

1. **الاطلاع على المهمة**: افتح ملف المهمة المعنية (مثال: `TASK-01-YOUSEF.md`).
2. **قراءة العقود المحددة**: تأكد من مراجعة قسم "اقرأ هذه الملفات أولاً" في ملف المهمة.
3. **استخدام الـ Prompt المرفق**: انسخ النص الموجود في قسم `Prompt خاص بالمهمة` إلى مساعد الذكاء الاصطناعي في Antigravity IDE دون تعديل في القيود.
4. **فحص الكود المنفذ**: راجع الملفات التي أنشأها أو عدلها الذكاء الاصطناعي وتأكد من مطابقتها التامة لمخطط قاعدة البيانات ورموز الأخطاء المعيارية في `docs/api-contract.md`.
5. **تشغيل الاختبارات**: تأكد من نجاح اختبارات Pytest.
6. **ملء تقرير التسليم**: انسخ `_integration/DELIVERY_TEMPLATE.md` إلى `_integration/Yousef/DELIVERY/DELIVERY-TASK-XX.md` واملأه كاملاً.
7. **إبلاغ القائد**: أبلغ قائد الفريق **أحمد العماري** بجاهزية المهمة للمراجعة.
