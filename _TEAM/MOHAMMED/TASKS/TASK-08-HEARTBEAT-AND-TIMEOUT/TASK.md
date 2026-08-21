# معالجة نبضات الـ Heartbeat ومهلة الانقطاع

## Task ID
`TASK-08-HEARTBEAT-AND-TIMEOUT`

## العضو المسؤول
محمد الداعس (Mohammed Al-Daees) - مهندس الويب سوكت

## الهدف
بناء معالج نبضات HEARTBEAT كل 30 ثانية وتحديث توقيت last_heartbeat وفصل الاتصالات الصامتة بعد 90 ثانية.

## وصف المهمة
بناء معالج نبضات HEARTBEAT كل 30 ثانية وتحديث توقيت last_heartbeat وفصل الاتصالات الصامتة بعد 90 ثانية.

## لماذا هذه المهمة مهمة للنظام
الحفاظ على قنوات الاتصال حية وإغلاق الاتصالات الميتة وتوفير موارد الخادم.

## المتطلبات الوظيفية
- استقبال HEARTBEAT وتحديث التوقيت في manager.
- فحص دوري أو عند الاستقبال لمهلة 90 ثانية وإغلاق القناة الصامتة.

## المتطلبات غير الوظيفية
- استقرار النظام على المدى الطويل.

## Edge Cases / الحالات الحدية
- عميل صامت لأكثر من 90 ثانية -> فصله وتنظيف الغرفة.

## الملفات المسموح بتعديلها
- `backend/app/websocket/router.py`
- `backend/app/websocket/manager.py`

## الملفات المسموح بإنشائها
- `backend/tests/websocket/test_websocket_heartbeat.py`

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
- رسائل HEARTBEAT.

## المخرجات المطلوبة
- إدارة مهلة النشاط وتحديث النبضات.

## نقاط التكامل مع أعضاء الفريق
- التكامل مع مؤقت useWebSocket في الواجهة.

## Dependencies
- TASK-07-TYPING-INDICATOR

## شروط اكتمال المهمة
- إدارة النبضات والمهلة بنجاح 100%.

## الاختبارات المطلوبة
- pytest backend/tests/websocket/test_websocket_heartbeat.py -v

## طريقة التسليم
- تقرير فحص الـ Heartbeat.

## ممنوعات المهمة
- ممنوع فصل الاتصالات النشطة التي ترسل نبضات بانتظام.
