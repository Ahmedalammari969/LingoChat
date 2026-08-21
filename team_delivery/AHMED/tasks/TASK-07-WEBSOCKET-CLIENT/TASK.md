# بناء عميل وخطاف الـ WebSocket والـ Heartbeat

## Task ID
`TASK-07-WEBSOCKET-CLIENT`

## العضو المسؤول
أحمد العماري (Ahmed Alammari) - قائد المشروع ومهندس الواجهات

## الهدف
تطوير خدمة عميل الويب سوكت في frontend/src/services/websocket.js وخطاف useWebSocket.js للاتصال بـ /ws/{room_id}?token=... وإرسال Heartbeat كل 30 ثانية وإعادة الاتصال التلقائي.

## وصف المهمة
تطوير خدمة عميل الويب سوكت في frontend/src/services/websocket.js وخطاف useWebSocket.js للاتصال بـ /ws/{room_id}?token=... وإرسال Heartbeat كل 30 ثانية وإعادة الاتصال التلقائي.

## لماذا هذه المهمة مهمة للنظام
توفير قناة اتصال حي مستقرة لتبادل الرسائل والأحداث اللحظية دون انقطاع.

## المتطلبات الوظيفية
- الاتصال بـ ws://localhost:8000/ws/{room_id}?token=${token}.
- إرسال نبضات HEARTBEAT كل 30 ثانية.
- إعادة الاتصال التلقائي الأسي (Exponential Backoff max 30s).
- دوال sendMessage و sendTyping واستقبال الأحداث.

## المتطلبات غير الوظيفية
- تنظيف المؤقتات وقناة الاتصال عند مغادرة الصفحة لمنع تسريب الذاكرة.

## Edge Cases / الحالات الحدية
- إغلاق الخادم بكود 4001 أو 4003 -> إيقاف إعادة الاتصال وتنبيه المستخدم.
- انقطاع الشبكة المؤقت.

## الملفات المسموح بتعديلها
- `frontend/src/services/websocket.js`
- `frontend/src/hooks/useWebSocket.js`
- `frontend/src/pages/ChatPage.jsx`

## الملفات المسموح بإنشائها
- `frontend/src/types/websocket.js`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/WEBSOCKET_CONTRACT.md`
- `_TEAM/00_SHARED/SECURITY_CONTRACT.md`

## الملفات الممنوع تعديلها
- `backend/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `WEBSOCKET_CONTRACT.md`
- `SECURITY_CONTRACT.md`

## المدخلات
- room_id, token, رسائل وأحداث المستخدم.

## المخرجات المطلوبة
- خدمة وخطاف WebSocket متين ومستقر.

## نقاط التكامل مع أعضاء الفريق
- يوفر الاتصال الحي لصفحة ChatPage.jsx.

## Dependencies
- TASK-06-CHAT-UI

## شروط اكتمال المهمة
- اتصال ويب سوكت مستقر يلتزم 100% بالعقد الرسمي.

## الاختبارات المطلوبة
- فحص عنوان الاتصال، مؤقت Heartbeat، معالجة أكواد الإغلاق، وفحص البناء.

## طريقة التسليم
- تقرير تسليم عميل الويب سوكت ونتائج البناء.

## ممنوعات المهمة
- ممنوع إرسال أي نوع رسالة غير الأنواع الستة المعتمدة.
