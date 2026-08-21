# بناء مدير اتصالات الويب سوكت

## Task ID
`TASK-03-CONNECTION-MANAGER`

## العضو المسؤول
محمد الداعس (Mohammed Al-Daees) - مهندس الويب سوكت

## الهدف
بناء وتطوير فئة ConnectionManager في backend/app/websocket/manager.py لإدارة اتصالات الغرف في الذاكرة وتتبع الاتصالات الحية وتوزيع الرسائل.

## وصف المهمة
بناء وتطوير فئة ConnectionManager في backend/app/websocket/manager.py لإدارة اتصالات الغرف في الذاكرة وتتبع الاتصالات الحية وتوزيع الرسائل.

## لماذا هذه المهمة مهمة للنظام
إدارة القنوات المفتوحة وعزل مستخدمي كل غرفة عن غيرها وإتاحة البث المتوازي.

## المتطلبات الوظيفية
- قاموس اتصالات الغرف room_id -> user_id -> ws.
- دوال connect و disconnect و broadcast_to_room.
- دالة record_heartbeat و get_active_connections_count.

## المتطلبات غير الوظيفية
- أمان التزامن ومعالجة انقطاع العملاء المفاجئ.

## Edge Cases / الحالات الحدية
- انقطاع عميل أثناء البث وتجاوزه بأمان.
- البث لغرفة فارغة دون أخطاء.

## الملفات المسموح بتعديلها
- `backend/app/websocket/manager.py`

## الملفات المسموح بإنشائها
- `backend/tests/unit/test_websocket_manager.py`

## الملفات التي يجب قراءتها أولاً
- `_TEAM/00_SHARED/WEBSOCKET_CONTRACT.md`

## الملفات الممنوع تعديلها
- `frontend/**`
- `backend/app/translation/**`
- `backend/app/database/**`
- `_TEAM/**`

## العقود التي يجب الالتزام بها
- `WEBSOCKET_CONTRACT.md`

## المدخلات
- كائنات WebSocket ومعرفات المستخدمين والغرف.

## المخرجات المطلوبة
- فئة ConnectionManager متكاملة.

## نقاط التكامل مع أعضاء الفريق
- تعتمد عليها حلقة أحداث WebSocket لبث الرسائل.

## Dependencies
- TASK-02-WEBSOCKET-PROTOCOL

## شروط اكتمال المهمة
- مدير اتصالات كفؤ ومستقر.

## الاختبارات المطلوبة
- pytest backend/tests/unit/test_websocket_manager.py -v

## طريقة التسليم
- تقرير فحص مدير الاتصالات ونتائج الاختبارات.

## ممنوعات المهمة
- ممنوع تسريب الرسائل بين غرف مختلفة.
