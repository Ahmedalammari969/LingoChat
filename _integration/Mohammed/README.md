# دليل مهام المطور: محمد الدعيـس (Mohammed Al-Daees)
# WebSocket & Real-Time Communication Engineering Guide

> **الدور الأساسي**: مهندس الاتصال الفوري والويب سوكت  
> **المسؤولية البرمجية**: WebSocket Protocol + Connection Manager + Real-Time Message Routing + Heartbeat & Lifecycle + Translation & Persistence Integration + WebSocket Tests  
> **المستندات المرجعية الأساسية**: `docs/websocket-contract.md` ، `docs/api-contract.md` ، `docs/translation-contract.md` ، `docs/security.md` ، `docs/architecture.md`

---

## 1. نطاق المسؤولية والملكية (Ownership)

### ما تملكه وتتحكم به بالكامل (Allowed Scope):
- بروتوكول ورسائل الويب سوكت: `backend/app/websocket/schemas.py`, `protocol.py`.
- مدير اتصالات الويب سوكت: `backend/app/websocket/manager.py`.
- مسار ومعالج الـ WebSocket الرئيسي: `backend/app/websocket/router.py`.
- اختبارات الـ WebSocket والاتصال الحي: `backend/tests/websocket/**`.

### ما لا تملكه ويمنع التعديل عليه (Forbidden Scope):
- **خدمة ومحركات الترجمة**: مملوكة لزميلك **مؤيد الصوفي** (`backend/app/translation/**`). يمكنك استدعاء `translate_message()` فقط من خلال واجهتها الرسمية.
- **قواعد البيانات وREST API**: مملوكة لزميلك **يوسف خيري** (`backend/app/database/**`, `backend/app/auth/**`, `backend/app/rooms/**`, etc.). يمكنك استدعاء دوال الـ Service المعتمدة فقط.
- **واجهة المستخدم Frontend**: مملوكة بالكامل للقائد **أحمد العماري** (`frontend/**`).

---

## 2. خريطة تسلسل المهام (Task Sequence)

| رقم المهمة | اسم المهمة | الملفات الأساسية | الأولوية |
| :--- | :--- | :--- | :--- |
| **TASK-01-MOHAMMED** | بروتوكول الويب سوكت ونماذج الرسائل والتحقق (WebSocket Protocol & Schemas) | `websocket/schemas.py`, `websocket/protocol.py`, `tests/unit/test_websocket_protocol.py` | حرجة |
| **TASK-02-MOHAMMED** | مدير الاتصالات ودورة الحياة والـ Heartbeat (Connection Manager) | `websocket/manager.py`, `tests/unit/test_websocket_manager.py` | حرجة |
| **TASK-03-MOHAMMED** | مسار الـ WebSocket والمصادقة والتحقق من العضوية (Router, Auth & Membership) | `websocket/router.py`, `tests/websocket/test_websocket_auth.py` | حرجة |
| **TASK-04-MOHAMMED** | معالجة الرسائل الحية والتوزيع والترجمة والانقطاع (Real-Time Messages & Translation Integration) | `websocket/router.py`, `websocket/manager.py`, `tests/websocket/test_websocket_messages.py` | حرجة |

---

## 3. قواعد حرجة خاصة بعقد WebSocket (Critical Contract Rules)

1. **الأنواع الستة الرسمية فقط للرسائل**:
   يسمح فقط بالأنواع التالية: `JOIN`, `LEAVE`, `TEXT_MESSAGE`, `TYPING`, `HEARTBEAT`, `ERROR`. يمنع منعاً باتاً إضافة أي نوع رسالة جديد دون موافقة القائد أحمد.
2. **هيكل الرسالة الموحد (Message Envelope)**:
   جميع الرسائل يجب أن تلتزم بالحقول الأربعة الإلزامية: `type`, `payload`, `timestamp`, `room_id`.
3. **أكواد إغلاق الاتصال الرسمية (Close Codes)**:
   - `4001`: غير مصرح (فشل مصادقة JWT).
   - `4003`: ممنوع (المستخدم ليس عضواً في الغرفة).
   - `4004`: الغرفة غير موجودة.
   - `1000`: إغلاق طبيعي.
4. **الحد الأقصى لحجم الرسالة**:
   الحد الأقصى لحجم الرسالة هو **4096 بايت** (UTF-8). أي رسالة تتجاوز ذلك ترفض فوراً بإرسال رسالة `ERROR` بكود `MESSAGE_TOO_LONG`.
5. **التعامل مع الترجمة**:
   الترجمة تتم لكل مستخدم مستقبل بحسب لغته المفضلة (`preferred_language`). في حال فشل الترجمة يتم تسليم الرسالة بنصها الأصلي مع إرسال رسالة خطأ تحذيرية.

---

## 4. إرشادات العمل اليومي واستخدام الذكاء الاصطناعي (AI Workflow)

1. افتح ملف المهمة المعنية (مثال: `TASK-01-MOHAMMED.md`).
2. راجع قسم `docs/websocket-contract.md` و `docs/security.md`.
3. انسخ نص الـ `Prompt خاص بالمهمة` بالكامل إلى الذكاء الاصطناعي في Antigravity IDE.
4. تحقق من مطابقة الرسائل والأكواد للعقد الرسمي.
5. شغل اختبارات Pytest وتأكد من نجاحها 100%.
6. املأ تقرير التسليم في `_integration/Mohammed/DELIVERY/DELIVERY-TASK-XX.md` وأبلغ القائد **أحمد العماري**.
