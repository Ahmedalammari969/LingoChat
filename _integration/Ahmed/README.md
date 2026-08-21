# دليل مهام قائد الفريق: أحمد العماري (Ahmed Alammari)
# Team Leader, Frontend Engineering & Final Integration Guide

> **الدور الأساسي**: قائد الفريق + مهندس الواجهات الأمامية + مسؤول الدمج الشامل والاختبار النهائي  
> **المسؤولية البرمجية**: Frontend (React/Vite) + API Client + Auth/Rooms/Chat/Dashboard UI + WebSocket Client Integration + End-to-End System Integration + Contract Auditing + Final Delivery Package  
> **المستندات المرجعية الأساسية**: كافة ملفات `docs/**` (`architecture.md`, `api-contract.md`, `websocket-contract.md`, `database-schema.md`, `translation-contract.md`, `security.md`)

---

## 1. نطاق المسؤولية والملكية (Ownership)

### ما تملكه وتتحكم به بالكامل (Allowed Scope):
- واجهة المستخدم وتجربة المستخدم بالكامل (React SPA): `frontend/src/**`.
- عميل الـ API والـ HTTP Client: `frontend/src/api/**`.
- خطافات الحالة والاتصال (Hooks): `frontend/src/hooks/**` (`useAuth.js`, `useWebSocket.js`).
- خدمات الواجهة والـ WebSocket Client: `frontend/src/services/**`.
- صفحات التطبيق والمكونات: `frontend/src/pages/**`, `frontend/src/components/**`.
- التنسيقات ونظام التصميم: `frontend/src/index.css`.
- إدارة ومراجعة واعتماد تقارير التسليم للفريق داخل: `_integration/**`.
- الدمج النهائي واختبارات النظام الشاملة (E2E & Smoke Tests).

### صلاحياتك القيادية (Leadership Scope):
- **المرجع النهائي للقرارات المعمارية**: أي تعارض أو غموض في العقود يتم حسمه حصرياً بقرار منك.
- **اعتماد التسليمات**: مراجعة تقارير `_integration/<Member>/DELIVERY/` والتأكد من مطابقة العقود ونجاح الاختبارات قبل دمج الكود.

---

## 2. خريطة تسلسل المهام (Task Sequence)

| رقم المهمة | اسم المهمة | الملفات الأساسية | الأولوية |
| :--- | :--- | :--- | :--- |
| **TASK-01-AHMED** | تهيئة بيئة الواجهات ونظام التصميم والعميل الأساسي (Frontend Foundation & API Client) | `frontend/src/index.css`, `frontend/src/api/client.js`, `frontend/src/types/*` | حرجة |
| **TASK-02-AHMED** | واجهات المصادقة وإدارة الجلسات و JWT (Authentication UI & State) | `frontend/src/pages/LoginPage.jsx`, `frontend/src/hooks/useAuth.js`, `frontend/src/services/auth.js` | حرجة |
| **TASK-03-AHMED** | واجهات استعراض وإنشاء والانضمام للغرف (Rooms Management UI) | `frontend/src/pages/RoomsPage.jsx`, `frontend/src/api/rooms.js` | عالية |
| **TASK-04-AHMED** | واجهة المحادثة متعددة اللغات وربط الـ WebSocket (Chat UI & Real-Time Hook) | `frontend/src/pages/ChatPage.jsx`, `frontend/src/hooks/useWebSocket.js`, `frontend/src/services/websocket.js` | حرجة جداً |
| **TASK-05-AHMED** | واجهة لوحة التحكم ومؤشرات النظام الحية (Dashboard UI & Stats Display) | `frontend/src/pages/DashboardPage.jsx`, `frontend/src/api/dashboard.js` | متوسطة |
| **TASK-06-AHMED** | الدمج النهائي الشامل والتدقيق على العقود (End-to-End Integration & Contract Audit) | `_integration/**`, Backend + Frontend Cross-Integration | حرجة جداً |
| **TASK-07-AHMED** | الاختبارات النهائية الشاملة وحزمة التسليم (Final Testing & Delivery Package) | Frontend & Backend Test Suites, Smoke Tests | حرجة |

---

## 3. إرشادات القيادة واستخدام الذكاء الاصطناعي (AI Workflow)

1. افتح ملف المهمة المعنية (مثال: `TASK-01-AHMED.md`).
2. تأكد من أن مهام الـ Backend التابعة لها قد تم تسليمها واعتمادها من زملائك.
3. انسخ نص الـ `Prompt خاص بالمهمة` إلى الذكاء الاصطناعي في Antigravity IDE.
4. تحقق من بناء واجهات غنية وتفاعلية (Dynamic, Responsive, Loading/Error states).
5. تأكد من تخزين رمز JWT في `localStorage` والتعامل الآمن معه دون طباعته.
6. شغل اختبارات الـ Frontend وتأكد من البناء `npm run build` دون أخطاء.
7. املأ تقرير التسليم في `_integration/Ahmed/DELIVERY/DELIVERY-TASK-XX.md`.
